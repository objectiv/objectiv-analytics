# Objectiv Bach: Pandas-like DataFrames backed by SQL

Bach is Objectiv's data modeling library. With Bach, you can compose models with familiar Pandas-like dataframe operations in your notebook. It uses an SQL abstraction layer that enables models to run on the full dataset. It includes a set of operations that enable effective feature creation for datasets that embrace the [open taxonomy of analytics](/schema/README.md).

Bach uses [`sql_models`](./sql_models/) under the hood, which makes it possible to easily build graphs of SQL models and generate SQL for the resulting composite `sql-models`. See [sql_models/README.md](./sql_models/README.md) for more information.

## Using Bach
To use Bach, use the following command:
```bash
pip install -e .
```
This will install Bach in edit mode, meaning you get the latest version from the local checkout.
For detailed installation & usage instructions, visit [Objectiv Docs](https://www.objectiv.io/docs).


## See Also
* [Pandas](https://github.com/pandas-dev/pandas): the inspiration for the API.
   Pandas has excellent [documentation](https://pandas.pydata.org/docs/) for its API.
* [SQL-models]((./sql_models/)): Sub-project that is used for generating the underlying sql-queries. Can be 
  found in the [`sql_models`](./sql_models/) package

## Support & Troubleshooting
If you need help using or installing Bach, join our [Slack channel](https://join.slack.com/t/objectiv-io/shared_invite/zt-u6xma89w-DLDvOB7pQer5QUs5B_~5pg) and post your question there. 

## Bug Reports & Feature Requests
If you’ve found an issue or have a feature request, please check out the [Contribution Guide](https://www.objectiv.io/docs/the-project/contributing.md).

## Security Disclosure
Found a security issue? Please don’t use the issue tracker but contact us directly. See [SECURITY.md](../SECURITY.md) for details.

## Custom development & contributing code
If you want to contribute to Objectiv or use it as a base for custom development, take a look at [CONTRIBUTING.md](CONTRIBUTING.md). It contains detailed development instructions and a link to information about our contribution process and where you can fit in.

## License
This repository is part of the source code for Objectiv, which is released under the Apache 2.0 License. Please refer to [LICENSE.md](../LICENSE.md) for details.

Unless otherwise noted, all files © 2021 Objectiv B.V.
