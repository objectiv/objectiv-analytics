"""CHECKLOCK HOLMES CLI
Usage:
    main.py [--engine=<engine>...] [--nb=<file>...] [--gh_issues_dir=<ghi>] [--dump_nb_scripts=<nbs_dir>]
    main.py -h | --help

Options:
    -h --help                   Show this screen.
    --engine=<engine>           Engines to run checks. Current supported engines: [{supported_engines}] [default: all]
    --nb=<file>                 Notebooks to be checked [default: {default_nb_dir}]
    --gh_issues_dir=<ghi>       Directory for logging github issues [default: {default_github_issues_dir}]
    -dump_nb_scripts<nbs_dir>   Directory where to dump notebook scripts
"""
from docopt import docopt

from checklock_holmes.models.nb_checker_models import NoteBookCheckSettings, NoteBookMetadata
from checklock_holmes.nb_checker import NoteBookChecker
from checklock_holmes.utils.constants import DEFAULT_NOTEBOOKS_DIR, DEFAULT_GITHUB_ISSUES_DIR
from checklock_holmes.utils.helpers import get_github_issue_filename, store_github_issue, store_nb_script
from checklock_holmes.utils.supported_engines import SupportedEngine


def check_notebooks(check_settings: NoteBookCheckSettings) -> None:
    checks = []
    github_issues_file_path = f'{check_settings.github_issues_dir}/{get_github_issue_filename()}'

    for nb in check_settings.notebooks_to_check:
        nb_checker = NoteBookChecker(metadata=NoteBookMetadata(path=nb))
        for engine in check_settings.engines_to_check:
            nb_check = nb_checker.check_notebook(engine)

            if nb_check.error:
                store_github_issue(nb_check, github_issues_file_path)

            if check_settings.dump_nb_scripts_dir:
                script_path = f'{check_settings.dump_nb_scripts_dir}/{nb_checker.metadata.name}_{engine}.py'
                store_nb_script(script_path, nb_checker.get_script(engine, is_execution=False))

            checks.append(nb_check)

    pe

if __name__ == '__main__':
    cli_docstring = __doc__.format(
        supported_engines=', '.join([engine for engine in SupportedEngine]),
        default_nb_dir=DEFAULT_NOTEBOOKS_DIR,
        default_github_issues_dir=DEFAULT_GITHUB_ISSUES_DIR,
    )
    arguments = docopt(cli_docstring, help=True, options_first=False)

    nb_check_settings = NoteBookCheckSettings(
        engines_to_check=arguments['--engine'],
        github_issues_dir=arguments['--gh_issues_dir'],
        dump_nb_scripts_dir=arguments['--dump_nb_scripts'],
        notebooks_to_check=arguments['--nb'],
    )
    check_notebooks(nb_check_settings)
