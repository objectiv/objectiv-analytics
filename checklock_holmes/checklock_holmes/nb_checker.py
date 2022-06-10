import json
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Dict, List

from checklock_holmes.models.nb_checker_models import CellError, NoteBookCheck
from checklock_holmes.utils.constants import (SET_ENV_VARIABLE_TEMPLATE,
                                              WRAPPED_CODE_TEMPLATE,
                                              SupportedEngine)
from settings import settings


@dataclass
class NoteBookChecker:
    notebook_path: str

    _errors: Dict[SupportedEngine, CellError] = field(default_factory=dict, init=False)

    @cached_property
    def cells(self) -> List[Dict[str, Any]]:
        with open(self.notebook_path) as nb_file:
            nb_data = json.load(nb_file)
            return nb_data.get('cells')

    def check_notebook(self, engine: SupportedEngine) -> NoteBookCheck:
        wrapped_script = self._get_script(engine, is_execution=True)
        completed = True
        try:
            exec(wrapped_script)
        except Exception:
            completed = False

        error = self._errors.get(engine)
        return NoteBookCheck(
            name=self.notebook_path,
            script=self._get_script(engine, is_execution=False),
            engine=engine,
            completed=completed,
            error=error,
            failing_block=''.join(self.cells[error.number]['source']) if error else None
        )

    @staticmethod
    def _log_wrapped_cell_code(cell_number: int, engine: str, source: List[str]) -> str:
        return WRAPPED_CODE_TEMPLATE.format(
            code_to_wrap='\t'.join(source),
            error_log_stmt=f'self._log_error({cell_number}, \"{engine}\",  e)',
        )

    def _log_error(self, cell_number: int, engine: SupportedEngine,  exc):
        self._errors[engine] = CellError(number=cell_number, exc=exc)

    def _get_script(self, engine, is_execution: bool = True) -> str:
        formatted_blocks = []
        for cell_num, cell_metadata in enumerate(self.cells):
            if cell_metadata['cell_type'] != 'code':
                continue

            if is_execution:
                formatted_block = self._log_wrapped_cell_code(
                    cell_num, engine, source=cell_metadata['source'],
                )
            else:
                formatted_block = f'# CELL {cell_num}\n' + ''.join(cell_metadata['source'])

            formatted_blocks.append(formatted_block)

        nb_script = '\n\n'.join(formatted_blocks)

        env_setup_bloc = self._get_env_setup_block(engine)
        return f'{env_setup_bloc}\n\n{nb_script}'

    @staticmethod
    def _get_env_setup_block(engine: SupportedEngine) -> str:
        env_variables = settings.get_env_variables(engine)
        env_variables_stmt = '\n'.join(
            [
                SET_ENV_VARIABLE_TEMPLATE.format(
                    env_var_name=env_var, env_var_value=val,
                )
                for env_var, val in env_variables.items()
            ]
        )
        return f"""
            # env variables setup
            import os
            {env_variables_stmt}
        """
