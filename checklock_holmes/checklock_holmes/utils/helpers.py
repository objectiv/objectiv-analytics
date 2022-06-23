"""
Copyright 2022 Objectiv B.V.
"""

from datetime import datetime
from typing import List

from tabulate import tabulate

from checklock_holmes.models.nb_checker_models import NoteBookCheck
from checklock_holmes.utils import constants


class CuriousIncident(Exception):
    def __init__(self, notebook_name: str, exc: Exception):
        super().__init__(f'{exc} that was the curious incident when executing {notebook_name} notebook')


def store_github_issue(nb_check: NoteBookCheck, github_issues_file: str) -> None:
    """
    If notebook check resulted with an error, it will add an issue to the final check's issue file.
    """
    if not nb_check.error:
        raise Exception('Cannot create issue for a check with no errors.')

    issue_md = constants.GITHUB_ISSUE_TEMPLATE.format(
        notebook=f'{nb_check.metadata.name}.{constants.NOTEBOOK_EXTENSION}',
        engine=nb_check.engine,
        cell_number=nb_check.error.number,
        failing_code=nb_check.failing_block,
        exception=nb_check.error.exc,
    )
    with open(github_issues_file, 'a') as file:
        file.write(issue_md)


def get_github_issue_filename() -> str:
    """
    Generates issue file name based on checking time.
    """
    current_check_time = datetime.now()
    return constants.GITHUB_ISSUE_FILENAME_TEMPLATE.format(
        date_str=current_check_time.strftime(constants.GTIHUB_ISSUE_DATE_STR_FORMAT)
    )


def store_nb_script(nb_scripts_path: str, script: str) -> None:
    """
    Stores the executed script for the notebook
    """
    with open(nb_scripts_path, 'w') as file:
        file.write(script)


def display_check_results(
    nb_checks: List[NoteBookCheck],
    github_files_path: str,
    display_cell_timings: bool,
) -> None:
    """
    Displays final report in console
    """
    data_to_show = []
    failed_checks = 0
    success_checks = 0
    skipped_checks = 0

    headers = constants.REPORT_HEADERS.copy()
    if display_cell_timings:
        headers.append(constants.ELAPSED_TIME_CELL_HEADER)

    for check in nb_checks:
        if check.error:
            failed_checks += 1
            status = 'failed'
        elif check.skipped:
            skipped_checks += 1
            status = 'skipped'
        else:
            success_checks += 1
            status = 'success'

        row = [
            check.metadata.name,
            check.engine,
            status,
            check.error.number if check.error else '',
            check.elapsed_time or '',
        ]
        if display_cell_timings and check.elapsed_time_per_cell:
            row.append('\n'.join(f'#{ct.number} - {ct.time}' for ct in check.elapsed_time_per_cell))

        data_to_show.append(row)

    print(tabulate(data_to_show, headers=headers, tablefmt="simple", floatfmt=".4f"))

    if success_checks:
        perc_success = round(success_checks/len(nb_checks) * 100, 2)
        print(constants.SUCCESS_CHECK_MESSAGE.format(
            success_checks=success_checks, perc_success=perc_success,
        ))

    if skipped_checks:
        perc_skipped = round(skipped_checks/len(nb_checks) * 100, 2)
        print(constants.SKIPPED_CHECK_MESSAGE.format(
            skipped_checks=skipped_checks, perc_skipped=perc_skipped,
        ))

    if failed_checks:
        perc_failed = round(failed_checks/len(nb_checks) * 100, 2)
        print(constants.FAILED_CHECK_MESSAGE.format(failed_checks=failed_checks, perc_failed=perc_failed))
        print(constants.MORE_INFORMATION_MESSAGE.format(github_issue_file=github_files_path))
