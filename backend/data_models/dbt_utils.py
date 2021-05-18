"""
Copyright 2021 Objectiv B.V.
"""
from typing import Optional, Dict

from dbt import tracking
from dbt.adapters.factory import get_adapter
from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.graph.parsed import ParsedModelNode
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


def get_sql_improved(model: str,
                     vars: Dict[str, str],
                     depth_ephemeral_models: Optional[int] = None) -> str:
    """
    Get the sql for a single model.

    WIP
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
    compiled_node = compiler.compile_node(node=node, manifest=manifest, extra_context=None, write=False)
    return compiled_node.compiled_sql


def set_previous_nodes_materialization(manifest: Manifest,
                                       graph: DiGraph,
                                       node: ParsedModelNode,
                                       depth: int):
    """
    Set node and the levels depth-1 below that to ephemeral, the level below depth-1 is set to view
    """
    if depth == 0:
        node.config.materialized = 'view'
        print(node.unique_id, node.config.materialized)
        return
    node.config.materialized = 'ephemeral'
    print(node.unique_id, node.config.materialized)
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

The ManifestLoader builds the manifest based on the files in the project-dir, and all includes projects.

## Task
The nodes are all put into a queue (in the right order).
The nodes are taken from the queue one by one, and for each a Runner is created that executes the part of
the overall Task that pertains to that node.
See dbt.task.runnable.GraphRunnableTask.run_queue

The Nodes contain information about whether the output should be ephemeral, so if we want to manipulate
that on the fly, we really need to work on the graph and node level.



## Tracking
A lot of the code in the main code is peppered with tracking statements, that call onto the snowplow
tracker to ship usage data back to DBT / fishtown. This sometimes makes the code a bit harder to
understand; just ignoring anything with `track` in the name makes it a bit easier to follow the code.
"""
