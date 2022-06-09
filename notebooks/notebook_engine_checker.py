import glob
import json
import os
from functools import cached_property
from typing import List, NamedTuple, Optional, Dict, Any

_ENV_VARIABLES_PER_ENGINE = {
    'postgres': {
        'DSN': os.environ.get('OBJ_DB_PG_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv')
    },
    'bigquery': {
        'DSN': os.environ.get('OBJ_DB_BQ_TEST_URL', 'bigquery://objectiv-snowplow-test-2/modelhub_test'),
        'GOOGLE_APPLICATION_CREDENTIALS': os.environ.get(
            'OBJ_DB_BQ_CREDENTIALS_PATH',
            os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            + '/modelhub/.secrets/bach-big-query-testing.json'
        ),
    }
}


class CellError(NamedTuple):
    number: int
    exc: Exception


class NoteBookCheck(NamedTuple):
    name: str
    script: str
    completed: bool
    engine: str
    error: Optional[CellError]
    failing_block: Optional[str]


class NoteBookChecker:
    def __init__(self, notebook_path: str) -> None:
        self._notebook_path = notebook_path
        self._errors = {}

    def _track_error(self, cell_number: int, engine: str,  exc):
        self._errors[engine] = CellError(cell_number, exc)

    def _wrap_cell_code(
        self, cell_number: int, engine: str, source: List[str]
    ) -> str:
        cell_code = '\t'.join(source)

        track_error_stmt = f'self._track_error({cell_number}, \"{engine}\",  e)'
        wrapped_code = (
            'try:\n'
            f'\t{cell_code}\n'
            'except Exception as e:\n'
            f'\t{track_error_stmt}\n'
            f'\traise Exception()'
        )
        return wrapped_code

    @cached_property
    def cells(self) -> List[Dict[str, Any]]:
        with open(self._notebook_path) as nb_file:
            nb_data = json.load(nb_file)
            return nb_data.get('cells')

    def _get_script(self, engine, wrapped: bool = True) -> str:
        formatted_blocks = []
        for cell_num, cell_metadata in enumerate(self.cells):
            if cell_metadata['cell_type'] != 'code':
                continue

            if wrapped:
                formatted_block = self._wrap_cell_code(
                    cell_num, engine, source=cell_metadata['source']
                )
            else:
                formatted_block = f'# CELL {cell_num}\n' + ''.join(cell_metadata['source'])

            formatted_blocks.append(formatted_block)

        nb_script = '\n\n'.join(formatted_blocks)
        return f'{self._get_env_setup_block(engine)}\n\n{nb_script}'

    @staticmethod
    def _get_env_setup_block(engine: str) -> str:
        env_variables_stmt = '\n'.join([
            f'os.environ[\'{env_var}\'] = \'{val}\''
            for env_var, val in _ENV_VARIABLES_PER_ENGINE[engine].items()
        ])
        return f'import os\n{env_variables_stmt}'

    def check_notebook(self, engine='postgres') -> NoteBookCheck:
        wrapped_script = self._get_script(engine, wrapped=True)
        completed = True
        try:
            exec(wrapped_script)
        except Exception:
            completed = False

        error = self._errors.get(engine)
        return NoteBookCheck(
            name=self._notebook_path,
            script=self._get_script(engine, wrapped=False),
            engine=engine,
            completed=completed,
            error=error,
            failing_block=''.join(self.cells[error.number]['source']) if error else None
        )


GITHUB_ISSUE_TEMPLATE = (
    '{notebook} notebook is failing for {engine} engine.\n'
    'Please check cell number: {cell_number}. \n'
    'Failing code:\n'
    '```python\n{code}\n```\n'
    'Raised exception: {exception}\n'
)


def _get_github_issues(nb_checks) -> List[str]:
    return [
        GITHUB_ISSUE_TEMPLATE.format(
            notebook=check.name,
            engine=check.engine,
            cell_number=check.error.number,
            code=check.failing_block,
            exception=check.error.exc,
        )
        for check in nb_checks if check.error
    ]


def check_notebooks():
    nb_checks = []
    for nb in glob.glob('*.ipynb'):
        checker = NoteBookChecker(notebook_path=nb)
        nb_checks += [
            checker.check_notebook(engine)
            for engine in _ENV_VARIABLES_PER_ENGINE
        ]

    gh_issues = _get_github_issues(nb_checks)
    print(gh_issues)


if __name__ == '__main__':
    check_notebooks()
