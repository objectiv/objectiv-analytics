"""
Copyright 2021 Objectiv B.V.


None of the code here is production ready. This is completely experimental.


Some of the code here is derived from DBT code, which is apache 2.0 licensed and copyrighted by
fishtown-analytics. See https://github.com/fishtown-analytics/dbt/commits/develop/License.md
"""
from copy import deepcopy
from typing import Optional, Dict, Any, List, cast, Tuple

from dbt import tracking
from dbt.adapters.factory import get_adapter
from dbt.clients import jinja
from dbt.compilation import Compiler, _extend_prepended_ctes, _add_prepended_cte
from dbt.contracts.graph.compiled import CompiledModelNode, InjectedCTE, COMPILED_TYPES, \
    NonSourceCompiledNode
from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.graph.parsed import ParsedModelNode
from dbt.exceptions import RuntimeException, InternalException
from dbt.main import parse_args
from dbt.task.compile import CompileTask
from dbt.tracking import User
from networkx import DiGraph


def get_compile_task(model: Optional[str], vars: Dict[str, str]) -> CompileTask:
    args = ['compile']
    if model:
        # we only support selecting a single model here (DBT will select all models that this one depends
        # on too). Note however that dbt has powerful selection semantics, we just don't use that here.
        # See https://docs.getdbt.com/reference/node-selection/syntax for more information.
        args += ['--models', model]
    if vars:
        vars_str = '{' + ', '.join([f'"{k}": "{v}"' for k, v in vars.items()]) + '}'
        args += ['--vars', vars_str]
    parsed = parse_args(args)
    task = CompileTask.from_args(parsed)
    return task


def get_sql(model: Optional[str], vars: Dict[str, str]) -> str:
    """
    Get the sql for a single model.

    NOTE: this function is still rather dumb. It basically runs 'dbt compile', and thus writes a lot of
    files to disk too as a side-effect.
    """
    # Make sure tracking is disabled
    tracking.active_user = User('')
    tracking.active_user.do_not_track = True

    task = get_compile_task(model, vars)
    result = task.run()

    if not result.results:
        raise Exception('No Results')
    last_result = result.results[-1]
    if not last_result.node.compiled_sql:
        raise Exception(f'No sql: {last_result}')
    return last_result.node.compiled_sql


def get_sql_improved(
        model: str,
        vars: Dict[str, str],
        model_specific_vars: Dict[str, Dict[str, str]] = None,
        depth_ephemeral_models: Optional[int] = 99
    ) -> str:
    """
    Get the sql for a single model, including all dependent models that are ephemeral.

    :param model: Short name of the model for which to get the sql. e.g. specify 'stats_per_feature_day'
        to indicate 'model.objectiv.stats_per_feature_day'
    :param vars: Dictionary mapping variable names to values. These values are global and are applied to
        all models, unless they are overridden.
    :param depth_ephemeral_models: Override for dbt settings regarding materializations. All recursively
        referenced models, x steps deep are set to be ephemeral.
    :param model_specific_vars: Override for the vars that only hold for a single model. Dictionary mapping
        the model name to a dictionary with key, values with model specific variables.

    :return: sql select query
    """
    tracking.active_user = User('')
    tracking.active_user.do_not_track = True

    # todo: get this through magic
    full_model_name = f'model.objectiv.{model}'

    ctask = get_compile_task(model, vars)
    # build manifest based on project files
    ctask.load_manifest()
    # build graph, does not compile individual nodes
    ctask.compile_manifest()

    manifest = ctask.manifest
    node = manifest.nodes[full_model_name]
    node.config.materialized = 'ephemeral'

    if depth_ephemeral_models is not None:
        set_previous_nodes_materialization(
            manifest=manifest,
            graph=ctask.graph.graph,
            node=node,
            depth=depth_ephemeral_models
        )

    adapter = get_adapter(ctask.config)
    compiler = adapter.get_compiler()
    # We want to call compiler.compile_node, but since that doesn't implement overriding variables per
    # model, we use our own custom_compile function instead.
    compiled_node = custom_compile(compiler=compiler, node=node, manifest=manifest, extra_context=None,
                                   model_specific_vars=model_specific_vars)
    return compiled_node.compiled_sql


def custom_compile(
        compiler: Compiler,
        node: ParsedModelNode,
        manifest: Manifest,
        extra_context: Optional[Dict[str, Any]] = None,
        model_specific_vars: Dict[str, Dict[str, str]] = None) -> CompiledModelNode:
    """
    Replacement for dbt.compilation.Compiler.compile_node that adds the possibility to set variables for
    specific models.
    """
    node = _custom_compile_node(compiler, node, manifest, extra_context, model_specific_vars)
    node, _ = _custom_recursively_prepend_ctes(compiler, node, manifest, extra_context, model_specific_vars)
    return node


def _custom_compile_node(compiler: Compiler,
                         node: ParsedModelNode,
                         manifest: Manifest,
                         extra_context: Optional[Dict[str, Any]] = None,
                         model_specific_vars: Dict[str, Dict[str, str]] = None) -> CompiledModelNode:
    """
    Replacement for dbt.compilation.Compiler._compile_node
    """
    if extra_context is None:
        extra_context = {}
    if model_specific_vars is None:
        model_specific_vars = {}

    print("Compiling {}".format(node.unique_id))

    data = node.to_dict(omit_none=True)
    data.update({
        'compiled': False,
        'compiled_sql': None,
        'extra_ctes_injected': False,
        'extra_ctes': [],
    })
    compiled_node = CompiledModelNode.from_dict(data)

    # change: check if variables are overridden
    # todo: don't use magic to get model_name, have a function for this
    model_name = node.unique_id.split('.')[-1]  # 'model.objectiv.x' -> 'x'
    if model_name in model_specific_vars and model_specific_vars[model_name]:
        config_copy = deepcopy(compiler.config)
        for var, value in model_specific_vars[model_name].items():
            config_copy.vars.vars[var] = value
        compiler_copy = Compiler(config_copy)
        context = compiler_copy._create_node_context(
            compiled_node, manifest, extra_context
        )
    else:
        # normal path: no variables overridden for this specific model
        context = compiler._create_node_context(
            compiled_node, manifest, extra_context
        )

    compiled_node.compiled_sql = jinja.get_rendered(
        node.raw_sql,
        context,
        node,
    )
    compiled_node.relation_name = compiler._get_relation_name(node)
    compiled_node.compiled = True

    return compiled_node


def _custom_recursively_prepend_ctes(
        compiler: Compiler,
        model: CompiledModelNode,
        manifest: Manifest,
        extra_context: Optional[Dict[str, Any]],
        model_specific_vars: Dict[str, Dict[str, str]] = None
    ) -> Tuple[CompiledModelNode, List[InjectedCTE]]:
    """
    Based on dbt.compilation.Compiler._recursively_prepend_ctes

    Main difference with the main method is that this calls _custom_compile_node instead of
    compiler._compile_node, but there are secondary changes too.

    Original docstring:
    This method is called by the 'compile_node' method. Starting
    from the node that it is passed in, it will recursively call
    itself using the 'extra_ctes'.  The 'ephemeral' models do
    not produce SQL that is executed directly, instead they
    are rolled up into the models that refer to them by
    inserting CTEs into the SQL.
    """
    if model.compiled_sql is None:
        raise RuntimeException(
            'Cannot inject ctes into an unparsed node', model
        )
    if model.extra_ctes_injected:
        return (model, model.extra_ctes)

    # Just to make it plain that nothing is actually injected for this case
    if not model.extra_ctes:
        model.extra_ctes_injected = True
        manifest.update_node(model)
        return (model, model.extra_ctes)

    # This stores the ctes which will all be recursively
    # gathered and then "injected" into the model.
    prepended_ctes: List[InjectedCTE] = []

    dbt_test_name = compiler._get_dbt_test_name()

    # extra_ctes are added to the model by
    # RuntimeRefResolver.create_relation, which adds an
    # extra_cte for every model relation which is an
    # ephemeral model.
    for cte in model.extra_ctes:
        if cte.id == dbt_test_name:
            sql = cte.sql
        else:
            if cte.id not in manifest.nodes:
                raise InternalException(
                    f'During compilation, found a cte reference that '
                    f'could not be resolved: {cte.id}'
                )
            cte_model = manifest.nodes[cte.id]

            if not cte_model.is_ephemeral_model:
                raise InternalException(f'{cte.id} is not ephemeral')

            # This model has already been compiled, so it's been
            # through here before
            if getattr(cte_model, 'compiled', False):
                assert isinstance(cte_model,
                                  tuple(COMPILED_TYPES.values()))
                cte_model = cast(NonSourceCompiledNode, cte_model)
                new_prepended_ctes = cte_model.extra_ctes

            # if the cte_model isn't compiled, i.e. first time here
            else:
                # This is an ephemeral parsed model that we can compile.
                # Compile and update the node
                cte_model = _custom_compile_node(compiler,
                    cte_model, manifest, extra_context, model_specific_vars)
                # recursively call this method
                cte_model, new_prepended_ctes = \
                    compiler._recursively_prepend_ctes(
                        cte_model, manifest, extra_context
                    )
                # Save compiled SQL file and sync manifest
                compiler._write_node(cte_model)
                manifest.sync_update_node(cte_model)

            _extend_prepended_ctes(prepended_ctes, new_prepended_ctes)

            new_cte_name = compiler.add_ephemeral_prefix(cte_model.name)
            rendered_sql = (
                cte_model._pre_injected_sql or cte_model.compiled_sql
            )
            sql = f' {new_cte_name} as (\n{rendered_sql}\n)'

        _add_prepended_cte(prepended_ctes, InjectedCTE(id=cte.id, sql=sql))

    injected_sql = compiler._inject_ctes_into_sql(
        model.compiled_sql,
        prepended_ctes,
    )
    model._pre_injected_sql = model.compiled_sql
    model.compiled_sql = injected_sql
    model.extra_ctes_injected = True
    model.extra_ctes = prepended_ctes
    model.validate(model.to_dict(omit_none=True))

    manifest.update_node(model)

    return model, prepended_ctes


def set_previous_nodes_materialization(manifest: Manifest,
                                       graph: DiGraph,
                                       node: ParsedModelNode,
                                       depth: int):
    """
    Set node and the levels depth-1 below that to ephemeral, the level below depth-1 is set to view
    """
    if depth == 0:
        node.config.materialized = 'view'
        return
    node.config.materialized = 'ephemeral'
    for prev_node_id in graph.pred[node.unique_id]:
        if prev_node_id not in manifest.nodes:
            # not a model node, perhaps a source or seed
            continue
        prev_node = manifest.nodes[prev_node_id]
        set_previous_nodes_materialization(manifest, graph, prev_node, depth-1)






"""
# Notes

## Global state:
* tracking
* flags
* log_manager
* ui
* current working directory


## Code flow:
main:main()
    -> rest of main: error and interrupt handling
    -> handle_and_check() - actual logic
        -> parse_args()
            - Use bog-standard python parsing to parser everything into a NameSpace object
                - Enrich file-paths to full paths
            - result contains `cls` which is the subtype of Task that must be run (note: this is the class
                object, not an instance of that class)
        -> initialize_config_values()
            - enable or disable tracking    - global setting
            - set some ui output settings   - global setting
        -> run_from_args(parsed)
            - flags.set_from_args(parsed)  - set global flags
            - cls.pre_init_hook(parsed)    - sets some global logging stuff
            -> task = cls.from_args(parsed)
                - create an instance of a specific Task sub-type; exact logic differs per Task type
                - The Task init takes two parameters: args and config
                    * args are the parsed arguments
                    * config is a configuration of type `Project` (or subclass `RuntimeConfig`). This
                        config is constructed based on the parsed arguments
                - global effect: move current working directory to project_dir
            -> task.run(): The run() implementation depends on the Task sub-type, for compile and run the
                    relevant implementation is dbt.task.runnable.GraphRunnableTask.run
                -> _runtime_initialize()
                    -> super()._runtime_initialize()
                         -> load_manifest()
                            -> ManifestLoader.get_full_manifest(self.config):
                                - projects = config.load_dependencies(): load all projects (e.g. other dbt_modules)
                                - loader = ManifestLoader(config, projects, macro_hook):
                                    Create a ManifestLoader. This constructor already might do i/o. if 'partial parsing' is enabled as flag or in the project settings
                                -> loader.load(): This is were all files get read, parsed and the graph constructed (TODO: check?)
                                    - per project: read all files (models, macros's, test, seed, docs, etc.)
                                    - parse all macros
                                    - reparse all macros and resolve dependencies between them
                                    # The macros need to be parsed before other files are parsed, because
                                    # other files might depend on them
                                    -> parse_project(project, files):
                                        parse all files in project, except for macros those are done already
                                    
                            - write_manifest(): write target/manifest.json
                         - compile_manifest()
                    - `self.job_queue = self.get_graph_queue()`: initialize the initial job-queue. The
                        get_graph_queue() implementation is Task-type dependent
                    - Fill self._flattened_nodes. It seems this contains the exact same nodes as
                        self.job_queue?!
                -> execute_with_hooks():
                        - selected_uids are the self._flattened_nodes
                    -> get_adapter(self.config): get database specific adapter (e.g. an adapter for Postgres)
                    -> before_run(adapter, selected_uids)
                    -> self.execute_nodes():
                        - Set up threads, if needed
                        -> run_queue(): Here the actually nodes get processed
                            - a node gets taken from the queue
                            - a Task-specific runner gets created for the node
                            - the runner is scheduled to execute:
                                single threaded:
                                -> call_runner()
                    -> after_run(adapter, result)
                    -> self.after_hooks(adapter, result, elapsed): print some stuff

## Manifest, Graph and Nodes
The Manifest object dbt.contracts.graph.manifest.Manifest contains the full graph of models that need to
be run. Each model being a node in the graph. A node is uniquely identified by it's name (e.g.
'model.objectiv.aggregated_features').

The ManifestLoader builds the manifest based on the files in the project-dir, and all included projects.

## Task
The nodes are all put into a queue (in the right order).
The nodes are taken from the queue one by one, and for each a Runner is created that executes the part of
the overall Task that pertains to that node.
See dbt.task.runnable.GraphRunnableTask.run_queue

The Nodes contain information about whether the output should be ephemeral, so if we want to manipulate
that on the fly, we really need to work on the graph and node level.



## Tracking
A lot of the code in the main code is peppered with tracking statements, that call onto the snowplow
tracker to ship usage data back to DBT / fishtown. This sometimes makes the code harder to understand; just
ignoring anything with `track` in the name makes it a bit easier to follow the code.
"""
