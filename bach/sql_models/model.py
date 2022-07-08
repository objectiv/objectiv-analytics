"""
Copyright 2021 Objectiv B.V.

Models:

* `SqlModel`: Actual sql-model. Instances of this class form the nodes in the model graph
* `SqlModelSpec`: Specification class, that specifies basic properties of an SqlModel instance
* `SqlModelBuilder`: Helper class to instantiate the (immutable) SqlModel objects. Generally models should
  extend this class and not the SqlModel class.
* `CustomSqlModelBuilder`: Utility child of SqlModelSpec that can be used to add a node with custom sql to a
  model graph.
* `Materialization`: Specifies what kind of SQL should be generated: a query or a specific create statement

"""
import collections
import hashlib
from abc import abstractmethod, ABCMeta
from copy import deepcopy
from enum import Enum
from typing import TypeVar, Generic, Dict, Any, Set, Tuple, Type, Union, Hashable, NamedTuple, Optional, \
    Mapping, MutableMapping, cast

from sql_models.constants import not_set, NotSet
from sql_models.util import extract_format_fields


class MaterializationType(NamedTuple):
    """
    type_name: unique identifier
    is_statement:
        True indicates that a SqlModel with this materialization should be turned into a sql statement,
            either query or a create statement
        False indicates that a SqlModel with this materialization should not be turned into a standalone sql
            statement. Example: a CTE should not be used as a standalone statement.
    is_cte:
        True indicates that a SqlModel with this materialization can be used as a CTE by another SqlModel.
        False indicates that a SqlModel with this materialization cannot be used as a CTE
    has_lasting_effect: true iff the materialization is a permanent table or view
    """
    type_name: str
    is_statement: bool
    is_cte: bool
    has_lasting_effect: bool


class Materialization(Enum):
    CTE = MaterializationType('cte', is_statement=False, is_cte=True, has_lasting_effect=False)
    """ A QUERY can be used as a CTE, but is also a stand-alone query."""
    QUERY = MaterializationType('query', is_statement=True, is_cte=True, has_lasting_effect=False)
    VIEW = MaterializationType('view', is_statement=True, is_cte=False, has_lasting_effect=True)
    TABLE = MaterializationType('table', is_statement=True, is_cte=False, has_lasting_effect=True)
    """
    TEMP TABLE is a temporary table that is limited to the current session, or a table that is guaranteed to
    be cleaned up by the database at some later time.
    """
    TEMP_TABLE = MaterializationType('temp_table', is_statement=True, is_cte=False, has_lasting_effect=False)
    """ A VIRTUAL_NODE will not be turned into a statement, nor generate any CTEs"""
    VIRTUAL_NODE = MaterializationType('virtual', is_statement=False, is_cte=False, has_lasting_effect=False)

    @property
    def type_name(self) -> str:
        """ Materialization type unique name e.g. 'cte' or 'table' """
        return self.value.type_name

    @property
    def is_statement(self) -> bool:
        return self.value.is_statement

    @property
    def is_cte(self) -> bool:
        return self.value.is_cte

    @property
    def has_lasting_effect(self) -> bool:
        return self.value.has_lasting_effect

    @classmethod
    def get_by_type_name(cls, type_name) -> 'Materialization':
        for mat in cls:
            if mat.type_name == type_name:
                return mat
        raise KeyError(f'no such Materialization: "{type_name}"')

    @classmethod
    def normalize(cls, materialization: Union['Materialization', str]) -> 'Materialization':
        if isinstance(materialization, str):
            return Materialization.get_by_type_name(materialization)
        if isinstance(materialization, Materialization):
            return materialization
        raise ValueError(f'materialization must be of type str or Materialization, '
                         f'encountered type: {type(materialization)}')


# special reference-level format string that will be filled in at sql-generation time with a per-model
# unique string
REFERENCE_UNIQUE_FIELD = 'id'


RefPath = Tuple[str, ...]

T = TypeVar('T', bound='SqlModelSpec')
TB = TypeVar('TB', bound='SqlModelBuilder')
TSqlModel = TypeVar('TSqlModel', bound='SqlModel')


class SqlModelSpec:
    """
    Abstract immutable class that specifies the sql, placeholders, and references that a
    SqlModel instance should have.

    Child classes need to define the actual template by implementing the sql, placeholders, and reference
    functions.

    Generally it's better to actually extend of the subclass ComposableSqlModel, as that has some methods
    to make it easier to instantiate an SqlModel based on the Template.
    """

    def __init__(self):
        # Basic check on the child-classes implementation of spec_references and spec_placeholders
        overlap = self.spec_references.intersection(self.spec_placeholders)
        if overlap:
            raise Exception(f'Specified reference names and specified placeholder names of class overlap.'
                            f'This indicates an error in the implementation of the'
                            f'{self.__class__.__name__} class. Overlap: {overlap}')

    @property
    def generic_name(self):
        """ Generic name. Can be overridden by subclasses. Must be a constant. """
        return self.__class__.__name__

    @property
    @abstractmethod
    def sql(self):
        """ Must be implemented by child class. Return value should typically be a constant. """
        raise NotImplementedError()

    @property
    @abstractmethod
    def spec_references(self) -> Set[str]:
        """ Must be implemented by child class. Return value should typically be a constant. """
        # TODO: add type information
        raise NotImplementedError()

    @property
    @abstractmethod
    def spec_placeholders(self) -> Set[str]:
        """ Must be implemented by child class. Return value should typically be a constant. """
        raise NotImplementedError()

    @staticmethod
    def placeholders_to_sql(placeholders: Mapping[str, Any]) -> Dict[str, str]:
        """
        Child classes can override this function if some of the placeholders require conversion before being
        used in format(). Should be a constant, pure, and immutable function.

        If any format string exists, and it should not be substituted in the reference resolving step,
        it should be escaped with escape_placeholder_value.
        """
        # Override for non-default behaviour
        # If we switch to jinja templates, then we won't need this function anymore.
        return {key: escape_placeholder_value(str(val)) for key, val in placeholders.items()}

    def assert_adheres_to_spec(self,
                               references: Mapping[str, 'SqlModel'],
                               placeholders: Mapping[str, Any]):
        """
        Verify that the references and placeholder values adhere to the specifications of self.
        :raise Exception: If a reference or placeholder value is missing
        """
        spec = self
        reference_keys = set(references.keys())
        placeholder_keys = set(placeholders.keys())
        # Allow for more references to be present, as they could've been added dynamically.
        if len(spec.spec_references - reference_keys) > 0:
            raise Exception(f'Provided references for model {spec.__class__.__name__} '
                            f'do not match required references: '
                            f'{sorted(reference_keys)} != {sorted(spec.spec_references)}')
        for reference_key, reference_value in references.items():
            if not isinstance(reference_value, SqlModel):
                raise Exception(f'Provided reference for model {spec.__class__.__name__} is not an '
                                f'instance of SqlModel. '
                                f'Reference: {reference_key}, type: {type(reference_value)}')
        if placeholder_keys != spec.spec_placeholders:
            raise Exception(f'Provided placeholders for model {spec.__class__.__name__} '
                            f'do not match required placeholders: '
                            f'{sorted(placeholder_keys)} != {sorted(spec.spec_placeholders)}')


class SqlModelBuilder(SqlModelSpec, metaclass=ABCMeta):
    """
    Extension of SqlModelSpec that adds functions to easily build an instance of
    SqlModel that uses the SqlModelSpec

    There are multiple ways to create an instance of a SqlModel:
        1) use build() on this class
        2.1) use instantiate_recursively() on an instance of this class
        2.2) use instantiate() on an instance of this class
        2.3) user __call__() on an instance of this class

    A single SqlModelBuilder can be used to instantiate multiple SqlModel models. If this
    class is used multiple times to create an instance with the same placeholders, references,
    and materialization, then the same instance is returned each time.
    """

    def __init__(self, **values: Any):
        # initialize values first, so any indirect calls to references and placeholders
        # in super.__init__() will work
        self._references: Dict[str, Union[SqlModelBuilder, SqlModel]] = {}
        self._placeholders: Dict[str, Any] = {}
        super().__init__()
        self.set_values(**values)
        self.materialization = Materialization.CTE
        self.materialization_name: Optional[str] = None
        self._cache_created_instances: Dict[str, 'SqlModel'] = {}

    @property
    def spec_references(self) -> Set[str]:
        """
        Automatically determine the reference names from the sql, which contains '{{reference}}' strings.
        """
        # get all format strings that are formatted as {{x}}, but explicitly remove the
        # REFERENCE_UNIQUE_FIELD, as it is a magic value that will be filled in later.
        return extract_format_fields(self.sql, 2) - {REFERENCE_UNIQUE_FIELD}

    @property
    def spec_placeholders(self) -> Set[str]:
        """
        Automatically determine the placeholder names from the sql, which contains '{placeholder}' strings.
        """
        return extract_format_fields(self.sql)

    @property
    def references(self):
        # return shallow-copy of the dictionary.
        # keys are strings and thus immutable, values are included uncopied.
        return {key: value for key, value in self._references.items()}

    @property
    def placeholders(self):
        # return deepcopy of the dictionary
        return deepcopy(self._placeholders)

    @classmethod
    def build(cls: Type[TB], **values) -> 'SqlModel[TB]':
        """
        Class method that instantiates this SqlModelBuilder class, and uses it to
        recursively instantiate SqlModel[T].

        This might mutate referenced SqlModelBuilder objects, see instantiate_recursively()
        for more information.
        """
        builder_instance: TB = cls(**values)
        return builder_instance.instantiate_recursively()

    def instantiate_recursively(self: TB) -> 'SqlModel[TB]':
        """
        Creates an instance of SqlModel[T] like instantiate(), but unlike instantiate()
        this will convert references that are SqlModelBuilder to SqlModel too.
        And this is done in a recursive manner. Note that this might thus recursively instantiate
        references and thus modify the .references of (indirectly) referenced SqlModelBuilder
        instances.

        :raise Exception: If there are cyclic references between the recursively referenced
            SqlBuilderModels
        """
        # Note: Although it is not possible to create cycles in the SqlModel graph (see docstring
        #   SqlModel), it is possible to create cycles between SqlModelBuilder instances. Python will raise
        #   an error when it sees unbounded recursion, so we actually don't need to check for that here.
        for reference_name in self._references.keys():
            reference_value = self._references[reference_name]
            if not isinstance(reference_value, SqlModel):
                if isinstance(reference_value, SqlModelBuilder):
                    self._references[reference_name] = reference_value.instantiate_recursively()
                else:
                    raise Exception(f'In class {self.__class__.__name__} the reference {reference_name} '
                                    f'is not an SqlModel, but of '
                                    f'type {type(reference_value)}.')
        return self.instantiate()

    def __call__(self: TB, **values) -> 'SqlModel[TB]':
        self.set_values(**values)
        return self.instantiate()

    def instantiate(self: TB) -> 'SqlModel[TB]':
        """
        Create an instance of SqlModel[TB] based on the placeholders, references,
        materialization, and placeholders_to_sql of self.

        If the exact same instance (as determined by result.hash) has been created already by this class,
        then that instance is returned and the newly created instance is discarded.
        """
        self._check_is_complete()
        instance = SqlModel(model_spec=self,
                            placeholders=self.placeholders,
                            references=self.references,
                            materialization=self.materialization,
                            materialization_name=self.materialization_name)
        # If we already once created the exact same instance, then we'll return that one and discard the
        # newly created instance.
        if instance.hash not in self._cache_created_instances:
            self._cache_created_instances[instance.hash] = instance
        return self._cache_created_instances[instance.hash]

    def set_values(self: TB, **values) -> TB:
        """
        Set values that can either be references or placeholders.
        If a value is a placeholder value then it must be immutable
        If a value is a reference then it must either be an instance of SqlModelBuilder or of SqlModel
        :param values:
        :return: self
        """
        for key, value in values.items():
            if key in self.spec_references:
                if not isinstance(value, (SqlModel, SqlModelBuilder)):
                    raise ValueError(f'reference ({key}) is of incorrect type: {type(value)}')
                self._references[key] = value
            elif key in self.spec_placeholders:
                # There is no straightforward way to check whether a value is immutable. However virtual
                # all immutable objects are also hashable, so we check that instead.
                if not isinstance(value, collections.abc.Hashable):
                    raise ValueError(f'placeholder ({key}) is of incorrect type: {type(value)}')
                self._placeholders[key] = value
            else:
                raise ValueError(f'Provided parameter {key} is not a valid placeholder nor reference for '
                                 f'class {self.__class__.__name__}. '
                                 f'Valid references: {self.spec_references}. '
                                 f'Valid placeholders: {self.spec_placeholders}.')
        return self

    def set_materialization(self: TB, materialization: Materialization) -> TB:
        """
        Set the materialization
        :return: self
        """
        self.materialization = materialization
        return self

    def set_materialization_name(self: TB, materialization_name: Optional[str]) -> TB:
        """
        Set the materialization_name
        :return: self
        """
        self.materialization_name = materialization_name
        return self

    def _check_is_complete(self):
        """
        Raises an Exception if either references or placeholder values are missing
        """
        self.assert_adheres_to_spec(references=self.references, placeholders=self.placeholders)


class SqlModel(Generic[T]):
    """
    An Immutable Sql Model consists of a sql select query, placeholder values and references to other
    Sql models.

    # Graphs of models
    The references to other models make it is possible to use the output of the sql queries of other models
    as the input for a new model. References link models in an directed-acyclic-graph, with the current
    model as starting point. If a model is referenced by other models, then its part of the graph of those
    models. A model will not be aware that it is part of another model's graph.

    # Immutability
    Instances of this class are immutable. This has a few desirable consequences:
        * A model can safely be used in another model's graph, as that other model can rely on the fact
            that the model won't change.
        * Each model calculates an md5-hash at initialization based on its own attributes and recursively
            referenced attributes. This hash only has to be calculated once, since all those (recursive)
            attributes are immutable. The hash can be used to identify identical models and used for
            optimizations when generating sql.
        * All references have to be set at initialization, the referenced objects have to be already
            initialized models, and references are unidirectional, therefore it is not possible to create
            cycles in the graph.
    """
    def __init__(self,
                 model_spec: T,
                 placeholders: Mapping[str, Hashable],
                 references: Mapping[str, 'SqlModel'],
                 materialization: Materialization,
                 materialization_name: Optional[str] = None
                 ):
        """
        :param model_spec: ModelSpec class defining the sql, and the names of the placeholders and references
            that this class must have.
        :param placeholders: Dictionary mapping placeholder names to placeholder values. Important: the
            values must be immutable. If not then the instance as a whole is not immutable, which will
            invalidate assumptions that code might hold about these instances. See the class's docstring
            for information on why this is important.
        :param references: Dictionary mapping reference names to instances of SqlModels.
        :param materialization: How this model should be materialized, e.g. as CTE, as a table, etc.
        :param materialization_name: If the materialization is a database object (e.g. table, view,
            temp table), then this value can be set to override the default name of the object.
        """
        self._model_spec = model_spec
        self._generic_name = model_spec.generic_name
        self._sql = model_spec.sql
        self._references: Mapping[str, 'SqlModel'] = references
        self._placeholders: Mapping[str, Any] = placeholders
        self._materialization = materialization
        self._materialization_name = materialization_name
        self._placeholder_formatter = model_spec.placeholders_to_sql

        # Verify completeness of this object: references and placeholders
        self._model_spec.assert_adheres_to_spec(references=self.references,
                                                placeholders=self.placeholders)
        # Calculate unique hash for this model's sql, placeholder values, materialization and references
        self._hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """
        Calculate md5 hash of the immutable data of this model that will be used for sql generation by the
        sql_generator. The hash is unique for the combination of the following attributes, and as such is
        unique for the sql that will be generated.
        Attributes considered in hash:
            1. generic_name
            2. sql
            3. placeholder values
            4. materialization
            5. references, and recursively their generic_name, sql, placeholder values, materialization,
                materialization_name, and recursive references
            6. materialization_name
        :return: 32 character string representation of md5 hash
        """
        data = {
            'generic_name': self.generic_name,
            'sql': self.sql,
            'properties': self.placeholders_formatted,
            'materialization': self.materialization.type_name,
            'references': {
                ref_name: model.hash for ref_name, model in self.references.items()
            }
        }
        if self.materialization_name is not None:
            data['materialization_name'] = self.materialization_name
        data_bytes = repr(data).encode('utf-8')
        return hashlib.md5(data_bytes).hexdigest()

    @property
    def model_spec(self):
        return deepcopy(self._model_spec)

    @property
    def generic_name(self) -> str:
        """ Name for the type of model."""
        return self._generic_name

    @property
    def materialization_name(self) -> Optional[str]:
        """ Optional name for this specific instance of the model_spec that this model implements. """
        return self._materialization_name

    @property
    def sql(self) -> str:
        return self._sql

    @property
    def references(self) -> MutableMapping[str, 'SqlModel']:
        # return shallow-copy of the dictionary.
        # keys are strings and thus immutable, values are included uncopied.
        return {key: value for key, value in self._references.items()}

    @property
    def placeholders(self) -> MutableMapping[str, Hashable]:
        # return deepcopy of the dictionary
        return cast(MutableMapping[str, Hashable], deepcopy(self._placeholders))

    @property
    def materialization(self) -> Materialization:
        return self._materialization

    @property
    def hash(self) -> str:
        """
        Unique 32 character hash based on this object's attributes and attributes of referenced models.
        If two instances have the same hash, they are equal for all intents and purposes,
        see _calculate_hash() for more information.

        This is different from the __hash__() function, which returns an integer, and is much more likely
        to collide.
        """
        return self._hash

    @property
    def placeholders_formatted(self) -> Dict[str, str]:
        return self._placeholder_formatter(self._placeholders)

    def copy_override(
        self: TSqlModel,
        *,
        model_spec: T = None,
        placeholders: Mapping[str, Hashable] = None,
        references: Mapping[str, 'SqlModel'] = None,
        materialization: Materialization = None,
        materialization_name: Union[Optional[str], NotSet] = not_set
    ) -> TSqlModel:
        """
        Create a copy of this instance, with the specified fields updated.
        Any fields that are not set will get the current value in the returned copy.

        Note that as None is a valid value for materialization_name, therefore we use the special token
        `not_set` to mean "keep current value".
        """
        materialization_name_value = \
            self.materialization_name if materialization_name is not_set else materialization_name
        return self.__class__(
            model_spec=self.model_spec if model_spec is None else model_spec,
            placeholders=self.placeholders if placeholders is None else placeholders,
            references=self.references if references is None else references,
            materialization=self.materialization if materialization is None else materialization,
            materialization_name=materialization_name_value
        )

    def copy_set(self: TSqlModel, new_placeholders: Mapping[str, Any]) -> TSqlModel:
        """
        Return a copy with the given placeholder values of this model updated.

        deprecated:: Use copy_override() if possible.
            https://github.com/objectiv/objectiv-analytics/issues/412
        """
        placeholders = self.placeholders
        for new_key, new_val in new_placeholders.items():
            if new_key not in placeholders:
                raise ValueError(f'Trying to update non-existing placeholder key: {new_key}. '
                                 f'placeholder keys: {sorted(placeholders.keys())}')
            placeholders[new_key] = new_val
        return self.copy_override(placeholders=placeholders)

    def copy_link(self: TSqlModel, new_references: Dict[str, 'SqlModel']) -> TSqlModel:
        """
        Create a copy with the given references of this model updated.

        Take care to not create cycles in the reference graph when using this function. Generally when
        working with a full graph of models its best to use the wrapper methods in graph_operations.py

        deprecated:: Use copy_override() if possible.
            https://github.com/objectiv/objectiv-analytics/issues/412
        """
        references = self.references
        for new_key, new_val in new_references.items():
            if new_key not in references:
                raise ValueError(f'Trying to update non-existing references key: {new_key}. '
                                 f'Reference keys: {sorted(references.keys())}')
            references[new_key] = new_val
        return self.copy_override(references=references)

    def copy_set_materialization(self: TSqlModel, materialization: Materialization) -> TSqlModel:
        """
        Create a copy with the given materialization of this model updated.

        deprecated:: Use copy_override() if possible.
            https://github.com/objectiv/objectiv-analytics/issues/412
        """
        if self.materialization == materialization:
            return self
        return self.copy_override(materialization=materialization)

    def copy_set_materialization_name(self: TSqlModel, materialization_name: Optional[str]) -> TSqlModel:
        """
        Create a copy with the given materialization_name of this model updated.

        deprecated:: Use copy_override() if possible.
            https://github.com/objectiv/objectiv-analytics/issues/412
        """
        if self.materialization_name == materialization_name:
            return self
        return self.copy_override(materialization_name=materialization_name)

    def set(self: TSqlModel,
            reference_path: RefPath,
            **placeholders) -> TSqlModel:
        """
        Create a (partial) copy of the graph that can be reached from self, with the placeholder values of
        the referenced node updated.

        The node identified by the reference_path is copied and updated, as are all nodes that
        (indirectly) refer that node. The updated version of self is returned.

        This instance, and all nodes that it refers recursively are unchanged.
        :param reference_path: references to traverse to get to the node that has to be updated
        :param placeholders: placeholder values to update
        :return: an updated copy of this node
        """
        # import locally to prevent cyclic imports
        from sql_models.graph_operations import get_node, replace_non_start_node_in_graph
        if reference_path == tuple():
            return self.copy_set(placeholders)
        replacement_model = get_node(self, reference_path).copy_set(placeholders)
        return replace_non_start_node_in_graph(self, reference_path, replacement_model)

    def link(self: TSqlModel,
             reference_path: RefPath,
             **references) -> TSqlModel:
        """
        Create a (partial) copy of the graph that can be reached from self, with the references of the
        referenced node updated.

        The node identified by the reference_path is copied and updated, as are all nodes that
        (indirectly) refer that node. The updated version of self is returned.

        This instance, and all nodes that it refers recursively are unchanged.
        :param reference_path: references to traverse to get to the node that has to be updated
        :param references: references to update
        :return: an updated copy of this node
        """
        # import locally to prevent cyclic imports
        from sql_models.graph_operations import get_node, replace_non_start_node_in_graph
        if reference_path == tuple():
            return self.copy_link(new_references=references)
        replacement_model = get_node(self, reference_path).copy_link(references)
        result = replace_non_start_node_in_graph(self, reference_path, replacement_model)
        return result

    def set_materialization(self: TSqlModel,
                            reference_path: RefPath,
                            materialization: Materialization) -> TSqlModel:
        """
        Create a (partial) copy of the graph that can be reached from self, with the materialization of the
        referenced node updated.

        The node identified by the reference_path is copied and updated, as are all nodes that
        (indirectly) refer that node. The updated version of self is returned.

        This instance, and all nodes that it refers recursively are unchanged.
        :param reference_path: references to traverse to get to the node that has to be updated
        :param materialization: materialization value
        :return: an updated copy of this node
        """
        # import locally to prevent cyclic imports
        from sql_models.graph_operations import get_node, replace_non_start_node_in_graph
        if reference_path == tuple():
            return self.copy_set_materialization(materialization)
        replacement_model = get_node(self, reference_path).copy_set_materialization(materialization)
        return replace_non_start_node_in_graph(self, reference_path, replacement_model)

    def set_materialization_name(self: TSqlModel,
                                 reference_path: RefPath,
                                 materialization_name: Optional[str]) -> TSqlModel:
        """
        Create a (partial) copy of the graph that can be reached from self, with the materialization_name of
        the referenced node updated.

        The node identified by the reference_path is copied and updated, as are all nodes that
        (indirectly) refer that node. The updated version of self is returned.

        This instance, and all nodes that it refers recursively are unchanged.
        :param reference_path: references to traverse to get to the node that has to be updated
        :param materialization_name: materialization_name value
        :return: an updated copy of this node
        """
        # import locally to prevent cyclic imports
        from sql_models.graph_operations import get_node, replace_non_start_node_in_graph
        if reference_path == tuple():
            return self.copy_set_materialization_name(materialization_name)
        replacement_model = get_node(self, reference_path).copy_set_materialization_name(
            materialization_name)
        return replace_non_start_node_in_graph(self, reference_path, replacement_model)

    def __eq__(self, other) -> bool:
        """
        Two SqlModels are equal if they have the same unique hash, and the same placeholder_formatter.
        This means the SqlModels effectively will lead to the same sql code when compiled. And
        additionally, derived models (e.g. through .set()) will be equal too if they are derived in the
        same way.

        This equality check does not take into account whether the classes are of the same (sub)class
        type, or whether the model_spec is the same type. As that ultimately won't affect the generated
        sql.
        """
        if not isinstance(other, SqlModel):
            return False
        # There is one edge-case (other than incredible unlikely md5 hash-collisions) where comparing the
        # hash to determine equality is not satisfactory. If a model has a non-standard
        # self._placeholder_formatter. Then the following scenario is possible:
        #   a.hash == b.hash
        #   c, d = a.set(tuple(), placeholder='new value'), b.set(tuple(), placeholder='new value')
        #   c.hash != d.hash
        # The same operation on two equal objects should render two equal objects again. By also including
        # the _placeholder_formatter in the comparison we can guarantee that.
        return self.hash == other.hash and self._placeholder_formatter == other._placeholder_formatter

    def __hash__(self) -> int:
        """ python hash. Must not be confused with the unique hash that is self.hash """
        return hash(self.hash)


class CustomSqlModelBuilder(SqlModelBuilder):
    """
    Builder that instantiates a SqlModel that can run custom sql and refer custom tables.
    """

    def __init__(self, sql: str, name: str = None):
        """
        :param sql: sql of the model
        :param name: optional override of the generic name (default: 'CustomSqlModel')
        """
        self._sql = sql
        if name:
            self._generic_name = name
        else:
            self._generic_name = 'CustomSqlModel'
        super().__init__()

    @property
    def sql(self):
        return self._sql

    @property
    def generic_name(self):
        return self._generic_name


def escape_raw_sql(sql: str) -> str:
    """
    Take any raw sql that will be used in a model and escape all '{' and '}'. This prevents the sql_generator
    from interpreting '{' and '}' as either placeholders or references.
    """
    return escape_format_string(sql, 2)


def escape_placeholder_value(value: str) -> str:
    """
    Take any value that will be used as a placeholder value, and escape all '{' and '}'. This prevents
    the sql_generator from interpreting '{' and '}' as references.
    """
    return escape_format_string(value, 1)


def escape_format_string(value: str, times=1) -> str:
    """
    Escape value for python's format() function. i.e. `escape_format_string(value).format() == value`.

    SqlModels.sql is formatted twice by the sql_generator.py's to_sql() function. Once to replace the
    placeholder values, and once to replace the references.
    So any raw sql that is part of a SqlModel.sql and contains either '{' or '}' should be escaped twice.
    Any values that get inserted by the first call to format (replacing the placeholders), should be escaped
    once.
    """
    for _ in range(times):
        value = value.replace('{', '{{').replace('}', '}}')
    return value
