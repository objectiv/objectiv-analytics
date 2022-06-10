from typing import List

from checklock_holmes.utils.constants import GITHUB_ISSUE_TEMPLATE


def get_github_issues(nb_checks) -> List[str]:
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
