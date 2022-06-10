import glob
import re
from typing import Optional, List, Union, Dict

from pydantic import BaseModel, validator

from checklock_holmes.utils.constants import NOTEBOOK_EXTENSION, NOTEBOOK_NAME_REGEX_PATTERN
from checklock_holmes.utils.supported_engines import SupportedEngine


class CellError(BaseModel):
    number: int
    exc: str


class NoteBookCheckSettings(BaseModel):
    engines_to_check: List[Union[str, SupportedEngine]]
    notebooks_to_check: List[str]
    github_issues_dir: str
    dump_nb_scripts_dir: Optional[str] = None

    @validator('engines_to_check')
    def _process_engines_to_check(cls, engines_to_check: List[str]) -> List[SupportedEngine]:
        return SupportedEngine.get_supported_engines(engines_to_check)

    @validator('notebooks_to_check')
    def _process_notebooks_to_check(cls, nb_to_check: List[str]) -> List[str]:
        processed_nb_to_check = []
        for nb_file in nb_to_check:
            if NOTEBOOK_EXTENSION not in nb_file:
                raise ValueError(f'{nb_file} must be .{NOTEBOOK_EXTENSION} extension.')

            if nb_file.endswith(f'*.{NOTEBOOK_EXTENSION}'):
                processed_nb_to_check.extend(glob.glob(nb_file))
            else:
                processed_nb_to_check.append(nb_file)

        return processed_nb_to_check


class NoteBookMetadata(BaseModel):
    path: str
    name: Optional[str]

    @validator('name', always=True)
    def _process_name(cls, val: Optional[str], values: Dict[str, Optional[str]]) -> str:
        path = values.get('path')
        return re.compile(NOTEBOOK_NAME_REGEX_PATTERN).match(path).group('nb_name')


class NoteBookCheck(BaseModel):
    metadata: NoteBookMetadata
    completed: bool
    engine: str
    error: Optional[CellError]
    failing_block: Optional[str]
