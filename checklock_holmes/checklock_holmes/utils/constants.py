# templates
GTIHUB_ISSUE_DATE_STR_FORMAT = '%Y%m%s_%H%M%S'
GITHUB_ISSUE_FILENAME_TEMPLATE = 'github_issue_{date_str}.md'
GITHUB_ISSUE_TEMPLATE = """
**[Notebook: {engine}]** {notebook} failing.
_____

Please check cell number: {cell_number}

Failing code:

```python
{failing_code}
```

Raised exception: 
{exception}
"""

WRAPPED_CODE_TEMPLATE = """
try:
    {code_to_wrap}
except Exception as e:
    {error_log_stmt}
    raise e
"""

SET_ENV_VARIABLE_TEMPLATE = 'os.environ["{env_var_name}"] = "{env_var_value}"'

# notebook check settings defaults
NOTEBOOK_EXTENSION = 'ipynb'
NOTEBOOK_NAME_REGEX_PATTERN = rf'(.*/)?(?P<nb_name>.+)(\.{NOTEBOOK_EXTENSION})'
DEFAULT_NOTEBOOKS_DIR = f'../notebooks/*.{NOTEBOOK_EXTENSION}'
DEFAULT_GITHUB_ISSUES_DIR = 'github_nb_issues'