import json
import re
import time
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Dict, List

from checklock_holmes.models.nb_checker_models import (
    CellError, NoteBookCheck, NoteBookMetadata
)
from checklock_holmes.settings import settings
from checklock_holmes.utils.constants import (
    NB_SCRIPT_TO_STORE_TEMPLATE, SET_ENV_VARIABLE_TEMPLATE,
    WRAPPED_CODE_TEMPLATE
)
from checklock_holmes.utils.supported_engines import SupportedEngine

_DEFAULT_ENV_VARIABLES = {
    'OBJECTIV_VERSION_CHECK_DISABLE': 'true'
}


@dataclass
class NoteBookChecker:
    MAX_LOG_EXCEPTION_MESSAGE = 500

    metadata: NoteBookMetadata

    _errors: Dict[SupportedEngine, CellError] = field(default_factory=dict, init=False)

    @cached_property
    def cells(self) -> List[Dict[str, Any]]:
        with open(self.metadata.path) as nb_file:
            nb_data = json.load(nb_file)
            return nb_data.get('cells')

    def check_notebook(self, engine: SupportedEngine) -> NoteBookCheck:
        wrapped_script = self.get_script(engine, is_execution=True)
        completed = True

        start_time = time.time()
        try:
            exec(wrapped_script)
        except Exception:
            completed = False
        end_time = time.time()

        error = self._errors.get(engine)
        return NoteBookCheck(
            metadata=self.metadata,
            engine=engine,
            completed=completed,
            error=error,
            failing_block=''.join(self.cells[error.number]['source']) if error else None,
            elapsed_time=end_time-start_time,
        )

    @staticmethod
    def _log_wrapped_cell_code(cell_number: int, engine: str, source: List[str]) -> str:
        return WRAPPED_CODE_TEMPLATE.format(
            code_to_wrap='    '.join(source),
            error_log_stmt=f'self._log_error({cell_number}, \"{engine}\",  e)',
        )

    def _log_error(self, cell_number: int, engine: SupportedEngine,  exc: Exception):
        self._errors[engine] = CellError(
            number=cell_number,
            exc=f'{exc.__class__.__name__}: {exc.args[0][:self.MAX_LOG_EXCEPTION_MESSAGE]}...'
        )

    def get_script(self, engine: SupportedEngine, is_execution: bool = True) -> str:
        formatted_blocks = []
        for cell_num, cell_metadata in enumerate(self.cells):
            if cell_metadata['cell_type'] != 'code':
                continue

            if is_execution:
                formatted_block = self._log_wrapped_cell_code(
                    cell_num, engine, source=cell_metadata['source'],
                )
            else:
                formatted_block = f'    # CELL {cell_num}\n    ' + '    '.join(cell_metadata['source'])

            formatted_blocks.append(formatted_block)

        nb_script = '\n\n'.join(formatted_blocks)
        if not is_execution and self.metadata.name:
            nb_script = NB_SCRIPT_TO_STORE_TEMPLATE.format(
                notebook=re.sub(r'(-|\s)+', '_', self.metadata.name),
                script=nb_script.strip(),
            )

        return f'{self._get_env_setup_block(engine)}\n\n{nb_script}'

    @staticmethod
    def _get_env_setup_block(engine: SupportedEngine) -> str:
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
