from datetime import datetime
from typing import Optional

from checklock_holmes.models.nb_checker_models import NoteBookCheck
from checklock_holmes.utils.constants import GITHUB_ISSUE_TEMPLATE, GITHUB_ISSUE_FILENAME_TEMPLATE, \
    GTIHUB_ISSUE_DATE_STR_FORMAT, NOTEBOOK_EXTENSION


def store_github_issue(nb_check: NoteBookCheck, github_issues_file: str) -> None:
    issue_md = GITHUB_ISSUE_TEMPLATE.format(
        notebook=f'{nb_check.metadata.name}.{NOTEBOOK_EXTENSION}',
        engine=nb_check.engine,
        cell_number=nb_check.error.number,
        failing_code=nb_check.failing_block,
        exception=nb_check.error.exc,
    )
    with open(github_issues_file, 'a') as file:
        file.write(issue_md)


def get_github_issue_filename() -> str:
    current_check_time = datetime.now()
    return GITHUB_ISSUE_FILENAME_TEMPLATE.format(
        date_str=current_check_time.strftime(GTIHUB_ISSUE_DATE_STR_FORMAT)
    )


def store_nb_script(nb_scripts_path: str, script: str) -> None:
    with open(nb_scripts_path, 'w') as file:
        file.write(script)
