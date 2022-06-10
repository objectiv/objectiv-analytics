from enum import Enum


class SupportedEngine(str, Enum):
    POSTGRES = 'postgres'
    BIGQUERY = 'bigquery'


GITHUB_ISSUE_TEMPLATE = """
[Notebook: {engine}] {notebook} failing.
Please check cell number: {cell_number}
Failing code:
```python
{failing_code}
```
Raised exception: {exception}
"""

WRAPPED_CODE_TEMPLATE = """
try:
    {code_to_wrap}
except Exception as e:
    {error_log_stmt}
    raise e
"""

SET_ENV_VARIABLE_TEMPLATE = 'os.environ["{env_var_name}"] = "{env_var_value}"'
