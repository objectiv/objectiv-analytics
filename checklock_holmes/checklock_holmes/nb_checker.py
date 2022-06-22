"""
Copyright 2022 Objectiv B.V.
"""
import json
import re
import time
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Dict, List

from checklock_holmes.models.nb_checker_models import (
    CellError, CellTiming, NoteBookCheck, NoteBookMetadata
)
from checklock_holmes.settings import settings
from checklock_holmes.utils.constants import (
    NB_SCRIPT_TO_STORE_TEMPLATE, SET_ENV_VARIABLE_TEMPLATE,
    TIMING_CELL_CODE_TEMPLATE, WRAPPED_CODE_TEMPLATE
)
from checklock_holmes.utils.helpers import CuriousIncident
from checklock_holmes.utils.supported_engines import SupportedEngine

_DEFAULT_ENV_VARIABLES = {
    'OBJECTIV_VERSION_CHECK_DISABLE': 'true'
}
_IGNORE_MARKDOWN_SQL_DISPLAYS = True


@dataclass
class NoteBookChecker:
    MAX_LOG_EXCEPTION_MESSAGE = 500

    metadata: NoteBookMetadata
    display_cell_timing: bool

    _errors: Dict[SupportedEngine, CellError] = field(default_factory=dict, init=False)
    _cell_timings: List[CellTiming] = field(default_factory=list, init=False)

    @cached_property
    def cells(self) -> List[Dict[str, Any]]:
        with open(self.metadata.path) as nb_file:
            nb_data = json.load(nb_file)
            return nb_data.get('cells')

    def check_notebook(self, engine: SupportedEngine) -> NoteBookCheck:
        """
        Creates and executes the notebook's script for the provided engine.

        Returns a generated report based on the execution.
        """
        # skip checks for engines without env variables
        if engine not in settings.engine_env_var_mapping:
            return NoteBookCheck(
                metadata=self.metadata,
                engine=engine,
                skipped=True,
            )

        self._cell_timings = []
        wrapped_script = self.get_script(engine, is_execution=True)
        completed = True

        start_time = time.time()
        try:
            exec(wrapped_script)
        except Exception as exc:
            if not self._errors.get(engine):
                raise CuriousIncident(notebook_name=self.metadata.name, exc=exc)

            completed = False
        end_time = time.time()

        error = self._errors.get(engine)
        return NoteBookCheck(
            metadata=self.metadata,
            engine=engine,
            completed=completed,
            error=error,
            failing_block=''.join(self.cells[error.number]['source']) if error else None,
            elapsed_time=end_time - start_time,
            elapsed_time_per_cell=self._cell_timings,
        )

    @staticmethod
    def _time_wrapped_cel_code(cell_number: int, code: str) -> str:
        """
        Wraps the cell's code for tracking the elapsed time on execution.
        """
        return TIMING_CELL_CODE_TEMPLATE.format(
            code_to_time=code,
            timing_stmt=f'self._log_cell_timing({cell_number}, elapsed_time)'
        )

    def _log_wrapped_cell_code(self, cell_number: int, engine: str, source: List[str]) -> str:
        """
        Wraps the cell's code for tracking raised exceptions on execution.
        """
        code = WRAPPED_CODE_TEMPLATE.format(
            code_to_wrap='    '.join(source),
            error_log_stmt=f'self._log_error({cell_number}, \"{engine}\",  e)',
        )
        if self.display_cell_timing:
            code = self._time_wrapped_cel_code(cell_number, code)

        return code

    def _log_error(self, cell_number: int, engine: SupportedEngine,  exc: Exception):
        """
        Logs raised exception when running the cell.
        """
        self._errors[engine] = CellError(
            number=cell_number,
            exc=f'{exc.__class__.__name__}: {str(exc)[:self.MAX_LOG_EXCEPTION_MESSAGE]}...'
        )

    def _log_cell_timing(self, cell_number: int, elapsed_time: int) -> None:
        """
        Logs the elapsed time for the cell's execution.
        """
        self._cell_timings.append(
            CellTiming(number=cell_number, time=elapsed_time)
        )

    def get_script(self, engine: SupportedEngine, is_execution: bool = True) -> str:
        """
        Extracts all code cells from the notebook and generates a script based on it.
        If is_execution is True, then code cells will be wrapped for error logging
        and (if required) timing loging. Otherwise, cells will be added as found in the notebook.

        When executing, we ignore cells containing only comments as this will generate errors when
        executing the script.
        """
        formatted_blocks = []
        for cell_num, cell_metadata in enumerate(self.cells):
            if cell_metadata['cell_type'] != 'code':
                continue

            if is_execution:
                source_without_comments_and_displays = [
                    stmt for stmt in cell_metadata['source']
                    if not (
                        stmt.startswith('#')
                        # avoid printing on console
                        or (_IGNORE_MARKDOWN_SQL_DISPLAYS and 'display_sql_as_markdown' in stmt)
                    )
                ]

                if not source_without_comments_and_displays:
                    continue

                formatted_block = self._log_wrapped_cell_code(
                    cell_num, engine, source=source_without_comments_and_displays,
                )

            else:
                formatted_block = f'    # CELL {cell_num}\n    ' + '    '.join(cell_metadata['source'])

            formatted_blocks.append(formatted_block)

        nb_script = '\n\n'.join(formatted_blocks)
        if not is_execution and self.metadata.name:
            # creates script for debugging
            # the template defines a function for the entire notebook
            # and adds a call to it in if __name__ == '__main__'
            nb_script = NB_SCRIPT_TO_STORE_TEMPLATE.format(
                notebook=re.sub(r'(-|\s)+', '_', self.metadata.name),
                script=nb_script.strip(),
            )

        return f'{self._get_env_setup_block(engine)}\n\n{nb_script}'

    @staticmethod
    def _get_env_setup_block(engine: SupportedEngine) -> str:
        """
        Returns the code block for setting env variables based on the engine to use.
        """
        env_variables = settings.get_env_variables(engine)
        env_variables.update(_DEFAULT_ENV_VARIABLES)
        env_variables_stmt = '\n'.join(
            [
                SET_ENV_VARIABLE_TEMPLATE.format(
                    env_var_name=env_var, env_var_value=val,
                )
                for env_var, val in env_variables.items()
            ]
        )
        return f'# env variables setup\nimport os\n{env_variables_stmt}'
