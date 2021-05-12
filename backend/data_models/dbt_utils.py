"""
Copyright 2021 Objectiv B.V.
"""
from typing import Optional, Dict

from dbt import tracking
from dbt.main import parse_args
from dbt.task.compile import CompileTask
from dbt.tracking import User


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


"""
# Notes

## Global state:
* tracking
* flags
* log_manager
* ui


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

## Nodes
DBT builds a dependency graph of all models. The nodes are all put into a queue (in the right order). The
nodes are taken from the queue one by one, and for each a Runner is created that executes the part of
the overall Task that pertains to that node.
See dbt.task.runnable.GraphRunnableTask.run_queue

The Nodes contain information about whether the output should be ephemeral, so if we want to manipulate
that on the fly, we really need to work on the graph and node level.



## Tracking
A lot of the code in the main code is peppered with tracking statements, that call onto the snowplow
tracker to ship usage data back to DBT / fishtown. This sometimes makes the code a bit harder to
understand; just ignoring anything with `track` in the name makes it a bit easier to follow the code.
"""
