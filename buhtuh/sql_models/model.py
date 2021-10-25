"""
Copyright 2021 Objectiv B.V.

Models:
* SqlModel         - Actual sql-model. Instances of this class form the nodes in the model graph
* SqlModelSpec     - Specification class, that specifies basic properties of an SqlModel instance
* SqlModelBuilder  - Helper class to instantiate the (immutable) SqlModel objects. Generally models should
                     extend this class and not the SqlModel class.
* CustomSqlModel   - Utility child of SqlModelSpec that can be used to add a node with custom sql to a
                     model graph.
"""
import hashlib
from abc import abstractmethod, ABCMeta
from copy import deepcopy
from enum import Enum
from typing import TypeVar, Generic, Dict, Any, Set, Tuple, Type, Union, TYPE_CHECKING, Sequence

from sql_models.util import extract_format_fields

if TYPE_CHECKING:
    from sql_models.expression import Expression


class Materialization(Enum):
    CTE = 1
    VIEW = 2


# special reference-level format string that will be filled in at sql-generation time with a per-model
# unique string
REFERENCE_UNIQUE_FIELD = 'id'


RefPath = Tuple[str, ...]

T = TypeVar('T', bound='SqlModelSpec')
TB = TypeVar('TB', bound='SqlModelBuilder')


class SqlModelSpec:
    """
    Abstract immutable class that specifies the sql, properties, and references that a
    SqlModel instance should have.

    Child classes need to define the actual template by implementing the sql, properties, and reference
    functions.

    Generally it's better to actually extend of the subclass ComposableSqlModel, as that has some methods
    to make it easier to instantiate an SqlModel based on the Template.
    """

    def __init__(self):
        # Basic check on the child-classes implementation of spec_references and spec_properties
        overlap = self.spec_references.intersection(self.spec_properties)
        if overlap:
            raise Exception(f'Specified reference names and specified property names of class overlap.'
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
    def spec_properties(self) -> Set[str]:
        """ Must be implemented by child class. Return value should typically be a constant. """
        raise NotImplementedError()

    @staticmethod
    def properties_to_sql(properties: Dict[str, Any]) -> Dict[str, str]:
        """
        Child classes can override this function if some of the properties require conversion before being
        used in format(). Should be a constant, pure, and immutable function.
        """
        # Override for non-default behaviour
        # If we switch to jinja templates, then we won't need this function anymore.
        return {key: str(val) for key, val in properties.items()}

    def assert_adheres_to_spec(self,
                               references: Dict[str, 'SqlModel'],
                               properties: Dict[str, Any]):
        """
        Verify that the references and properties adhere to the specifications of self.
        :raise Exception: If a reference or property is missing
        """
        spec = self
        reference_keys = set(references.keys())
        property_keys = set(properties.keys())
        if reference_keys != spec.spec_references:
            raise Exception(f'Provided references for model {spec.__class__.__name__} '
                            f'do not match required references: '
                            f'{sorted(reference_keys)} != {sorted(spec.spec_references)}')
        for reference_key, reference_value in references.items():
            if not isinstance(reference_value, SqlModel):
                raise Exception(f'Provided reference for model {spec.__class__.__name__} is not an '
                                f'instance of SqlModel. '
                                f'Reference: {reference_key}, type: {type(reference_value)}')
        if property_keys != spec.spec_properties:
            raise Exception(f'Provided properties for model {spec.__class__.__name__} '
                            f'do not match required properties: '
                            f'{sorted(property_keys)} != {sorted(spec.spec_properties)}')


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
    class is used multiple times to create an instance with the same properties, references,
    and materialization, then the same instance is returned each time.
    """

    def __init__(self, **values: Any):
        # initialize values first, so any indirect calls to references and properties
        # in super.__init__() will work
        self._references: Dict[str, Union[SqlModelBuilder, SqlModel]] = {}
        self._properties: Dict[str, Any] = {}
        super().__init__()
        self.set_values(**values)
        self.materialization = Materialization.CTE
        self._cache_created_instances: Dict[str, 'SqlModel'] = {}

    @property
    def spec_references(self) -> Set[str]:
        """
        Automatically determine the reference names from the sql property.
        """
        # get all format strings that are formatted as {{x}}, but explicitly remove the
        # REFERENCE_UNIQUE_FIELD, as it is a magic value that will be filled in later.
        return extract_format_fields(self.sql, 2) - {REFERENCE_UNIQUE_FIELD}

    @property
    def spec_properties(self) -> Set[str]:
        """
        Automatically determine the property names from the sql property.
        """
        return extract_format_fields(self.sql)

    @property
    def references(self):
        # return shallow-copy of the dictionary.
        # keys are strings and thus immutable, values are included uncopied.
        return {key: value for key, value in self._references.items()}

    @property
    def properties(self):
        # return deepcopy of the dictionary
        return deepcopy(self._properties)

    @classmethod
    def build(cls: Type[T], **values) -> 'SqlModel[TB]':
        """
        Class method that instantiates this SqlModelBuilder class, and uses it to
        recursively instantiate SqlModel[T].

        This might mutate referenced SqlModelBuilder objects, see instantiate_recursively()
        for more information.
        """
        builder_instance: TB = cls(**values)  # type: ignore
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

    def __call__(self: TB, **values: Union[int, str, 'Expression', Sequence['Expression'],
                                           'SqlModel', 'SqlModelBuilder']) -> 'SqlModel[TB]':
        self.set_values(**values)
        return self.instantiate()

    def instantiate(self: TB) -> 'SqlModel[TB]':
        """
        Create an instance of SqlModel[T] based on the properties, references,
        materialization, and properties_to_sql of self.

        If the exact same instance (as determined by result.hash) has been created already by this class,
        then that instance is returned and the newly created instance is discarded.
        """
        self._check_is_complete()
        instance = SqlModel(model_spec=self,
                            properties=self.properties,
                            references=self.references,
                            materialization=self.materialization)
        # If we already once created the exact same instance, then we'll return that one and discard the
        # newly created instance.
        if instance.hash not in self._cache_created_instances:
            self._cache_created_instances[instance.hash] = instance
        return self._cache_created_instances[instance.hash]

    def set_values(self: TB, **values: Union[int, str, 'Expression', Sequence['Expression'],
                                             'SqlModel', 'SqlModelBuilder']) -> TB:
        """
        Set values that can either be references or properties
        :param values:
        :return: self
        """
        # todo: check that values are of the correct types
        from sql_models.expression import Expression

        for key, value in values.items():
            if key in self.spec_references:
                if not isinstance(value, (SqlModel, SqlModelBuilder)):
                    raise ValueError(f'reference of incorrect type: {type(value)}')
                self._references[key] = value
            elif key in self.spec_properties:
                if isinstance(value, list):
                    self._properties[key] = ", ".join([v.to_sql() for v in value])
                else:
                    if isinstance(value, Expression):
                        self._properties[key] = value.to_sql()
                    elif isinstance(value, (int, str)):
                        self._properties[key] = value
                    else:
                        raise ValueError(f'value type should be int, str or Expression but got {type(value)}')
            else:
                raise ValueError(f'Provided parameter {key} is not a valid property nor reference for '
                                 f'class {self.__class__.__name__}. '
                                 f'Valid references: {self.spec_references}. '
                                 f'Valid properties: {self.spec_properties}.')
        return self

    def set_materialization(self: TB, materialization: Materialization) -> TB:
        """
        Set the materialization
        :return: self
        """
        self.materialization = materialization
        return self

    def _check_is_complete(self):
        """
        Raises an Exception if either references or properties are missing
        """
        self.assert_adheres_to_spec(references=self.references, properties=self.properties)


class SqlModel(Generic[T]):
    """
    An Immutable Sql Model consists of a sql select query, properties and references to other Sql models.

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
                 properties: Dict[str, Any],
                 references: Dict[str, 'SqlModel'],
                 materialization: Materialization
                 ):
        """
        :param model_spec: ModelSpec class defining the sql, and the names of the properties and references
            that this class must have.
        :param properties: Dictionary mapping property names to property values
        :param references: Dictionary mapping reference names to instances of SqlModels.
        """
        self._model_spec = model_spec
        self._generic_name = model_spec.generic_name
        self._sql = model_spec.sql
        self._references: Dict[str, 'SqlModel'] = references
        self._properties: Dict[str, Any] = properties
        self._materialization = materialization
        self._property_formatter = model_spec.properties_to_sql

        # Verify completeness of this object: references and properties
        self._model_spec.assert_adheres_to_spec(references=self.references,
                                                properties=self.properties)
        # Calculate unique hash for this model's sql, properties, materialization and references
        self._hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """
        Calculate md5 hash of the immutable data of this model that will be used for sql generation by the
        sql_generator. The hash is unique for the combination of the following attributes, and as such is
        unique for the sql that will be generated.
        Attributes considered in hash:
            1. generic_name
            2. sql
            3. properties
            4. materialization
            5. references, and recursively their sql, properties, materialization, and their references
        :return: 32 character string representation of md5 hash
        """
        data = {
            'generic_name': self.generic_name,
            'sql': self.sql,
            'properties': self.properties_formatted,
            'materialization': self.materialization.value,
            'references': {
                ref_name: model.hash for ref_name, model in self.references.items()
            }
        }
        data_bytes = repr(data).encode('utf-8')
        return hashlib.md5(data_bytes).hexdigest()

    @property
    def generic_name(self) -> str:
        return self._generic_name

    @property
    def sql(self) -> str:
        return self._sql

    @property
    def references(self) -> Dict[str, 'SqlModel']:
        # return shallow-copy of the dictionary.
        # keys are strings and thus immutable, values are included uncopied.
        return {key: value for key, value in self._references.items()}

    @property
    def properties(self) -> Dict[str, Any]:
        # return deepcopy of the dictionary
        return deepcopy(self._properties)

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
    def properties_formatted(self) -> Dict[str, str]:
        return self._property_formatter(self._properties)

    def copy_set(self, new_properties: Dict[str, Any]) -> 'SqlModel[T]':
        """
        Return a copy with the given properties of this model updated.
        """
        references = self.references
        properties = self.properties
        for new_key, new_val in new_properties.items():
            if new_key not in properties:
                raise ValueError(f'Trying to update non-existing property key: {new_key}. '
                                 f'Property keys: {sorted(properties.keys())}')
            properties[new_key] = new_val
        return SqlModel(
            model_spec=self._model_spec,
            references=references,
            properties=properties,
            materialization=self.materialization
        )

    def copy_link(self,
                  new_references: Dict[str, 'SqlModel']) -> 'SqlModel[T]':
        """
        Create a copy with the given references of this model updated.

        Take care to not create cycles in the reference graph when using this function. Generally when
        working with a full graph of models its best to use the wrapper methods in graph_operations.py
        """
        references = self.references
        properties = self.properties
        for new_key, new_val in new_references.items():
            if new_key not in references:
                raise ValueError(f'Trying to update non-existing references key: {new_key}. '
                                 f'Reference keys: {sorted(references.keys())}')
            references[new_key] = new_val
        return SqlModel(
            model_spec=self._model_spec,
            references=references,
            properties=properties,
            materialization=self.materialization
        )

    def copy_set_materialization(self, materialization: Materialization) -> 'SqlModel[T]':
        """
        Create a copy with the given materialization of this model updated.
        """
        if self.materialization == materialization:
            return self
        references = self.references
        properties = self.properties
        return SqlModel(
            model_spec=self._model_spec,
            references=references,
            properties=properties,
            materialization=materialization
        )

    def set(self,
            reference_path: RefPath,
            **properties) -> 'SqlModel[T]':
        """
        Create a (partial) copy of the graph that can be reached from self, with the properties of the
        referenced node updated.

        The node identified by the reference_path is copied and updated, as are all nodes that
        (indirectly) refer that node. The updated version of self is returned.

        This instance, and all nodes that it refers recursively are unchanged.
        :param reference_path: references to traverse to get to the node that has to be updated
        :param properties: properties to update
        :return: an updated copy of this node
        """
        # import locally to prevent cyclic imports
        from sql_models.graph_operations import get_node, replace_node_in_graph
        replacement_model = get_node(self, reference_path).copy_set(properties)
        return replace_node_in_graph(self, reference_path, replacement_model)

    def link(self,
             reference_path: RefPath,
             **references) -> 'SqlModel[T]':
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
        from sql_models.graph_operations import get_node, replace_node_in_graph
        replacement_model = get_node(self, reference_path).copy_link(references)
        return replace_node_in_graph(self, reference_path, replacement_model)

    def set_materialization(self,
                            reference_path: RefPath,
                            materialization: Materialization) -> 'SqlModel[T]':
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
        from sql_models.graph_operations import get_node, replace_node_in_graph
        replacement_model = get_node(self, reference_path).copy_set_materialization(materialization)
        return replace_node_in_graph(self, reference_path, replacement_model)

    def __eq__(self, other) -> bool:
        """
        Two SqlModels are equal if they have the same unique hash, and the same property_formatter.
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
        # self._property_formatter. Then the following scenario is possible:
        #   a.hash == b.hash
        #   c, d = a.set(tuple(), property='new value'), b.set(tuple(), property='new value')
        #   c.hash != d.hash
        # The same operation on two equal objects should render two equal objects again. By also including
        # the _property_formatter in the comparison we can guarantee that.
        return self.hash == other.hash and self._property_formatter == other._property_formatter

    def __hash__(self) -> int:
        """ python hash. Must not be confused with the unique hash that is self.hash """
        return hash(self.hash)


class CustomSqlModel(SqlModelBuilder):
    """
    Model that can run custom sql and refer custom tables.
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
            self._generic_name = self.__class__.__name__
        super().__init__()

    @property
    def sql(self):
        return self._sql

    @property
    def generic_name(self):
        return self._generic_name
