# Objectiv Bach: Pandas-like DataFrames backed by SQL

Bach is a python-based data modeling library that enables you to use Pandas-like operations that run on your full dataset in the SQL database. Any dataframe or model built with Bach can be converted to an SQL statement with a single command. It includes a set of operations that enable effective feature creation for data sets that embrace the [open analytics taxonomy](https://objectiv.io/docs/taxonomy/).

Bach uses [`sql_models`](./sql_models/) under the hood, which makes it possible to easily build graphs of SQL models and generate SQL for the resulting composite `sql-models`. See [sql_models/README.md](./sql_models/README.md) for more information.

Visit [Objectiv Docs](https://objectiv.io/docs/modeling/bach/) to learn more

## Using Bach
To use Bach, use the following command:
```bash
pip install objectiv-bach
```

If you want the latest and greatest from your local checkout, install objectiv_bach in edit mode:
```bash
pip install -e .
```

This will install Bach in edit mode, meaning you get the latest version from the local checkout.
For detailed installation & usage instructions, visit [Objectiv Docs](https://www.objectiv.io/docs).


## Running Functional and Unit Tests
In case you are interested on running tests, install all requirements from ``requirements-dev.txt``

### Setting up environmental variables
Functional tests require reading from multiple databases, in order to run them you should define
any of the following variables (based on the engine you want to test):

|    Database     |                  |           Variables          |
|:---------------:|------------------|:----------------------------:|
|    Postgres     | Database URL     |     `OBJ_DB_PG_TEST_URL`     |
|    BigQuery     | Database URL     |     `OBJ_DB_BQ_TEST_URL`     |
|    BigQuery     | Credentials Path | `OBJ_DB_BQ_CREDENTIALS_PATH` |



### Running Postgres-only tests
For running tests for Postgres, run the following command:
```bash
make tests
```

### Running BigQuery-only tests
Before running tests for BigQuery, please make sure you have the following tables in your dataset:

**Cities**
```sql
insert into `<YOUR_PROJECT>.<YOUR_DATASET>.cities`(skating_order, city, municipality, inhabitants, founding)
values
    (1, 'Ljouwert', 'Leeuwarden', 93485, 1285),
    (2, 'Snits', 'Súdwest-Fryslân', 33520, 1456),
    (3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268),
    (4, 'Sleat', 'De Friese Meren', 700, 1426),
    (5, 'Starum', 'Súdwest-Fryslân', 960, 1061),
    (6, 'Hylpen', 'Súdwest-Fryslân', 870, 1225),
    (7, 'Warkum', 'Súdwest-Fryslân', 4440, 1399),
    (8, 'Boalsert', 'Súdwest-Fryslân', 10120, 1455),
    (9, 'Harns', 'Harlingen', 14740, 1234),
    (10, 'Frjentsjer', 'Waadhoeke', 12760, 1374),
    (11, 'Dokkum', 'Noardeast-Fryslân', 12675, 1298);
```
**Foods**
```sql
insert into `<YOUR_PROJECT>.<YOUR_DATASET>.foods`(skating_order, food, moment, date)
values
    (1, 'Sûkerbôlle', '2021-05-03 11:28:36.388', '2021-05-03'),
    (2, 'Dúmkes', '2021-05-04 23:28:36.388', '2021-05-04'),
    (4, 'Grutte Pier Bier', '2022-05-03 14:13:13.388', '2022-05-03');
```
**Railways**
```sql
insert into `<YOUR_PROJECT>.<YOUR_DATASET>.railways`(station_id, town, station, platforms)
values
    (1, 'Drylts', 'IJlst', 1),
    (2, 'It Hearrenfean', 'Heerenveen', 1),
    (3, 'It Hearrenfean', 'Heerenveen IJsstadion', 2),
    (4, 'Ljouwert', 'Leeuwarden', 4),
    (5, 'Ljouwert', 'Camminghaburen', 1),
    (6, 'Snits', 'Sneek', 2),
    (7, 'Snits', 'Sneek Noord', 2);
```

After setting up your tables, run the following command:
```bash
make tests-big-query
```

### Running tests for all databases
In case you want to run all tests for multiple database, run the following command:
```bash
make tests-all
```

## See Also
* [Pandas](https://github.com/pandas-dev/pandas): the inspiration for the API.
   Pandas has excellent [documentation](https://pandas.pydata.org/docs/) for its API.
* [SQL-models](./sql_models/): Sub-project that is used for generating the underlying sql-queries. Can be 
  found in the [`sql_models`](./sql_models/) package

## Support & Troubleshooting
If you need help using or installing Bach, join our [Slack channel](https://objectiv.io/join-slack/) and post your question there. 

## Bug Reports & Feature Requests
If you’ve found an issue or have a feature request, please check out the [Contribution Guide](https://objectiv.io/docs/home/the-project/contribute/).

## Security Disclosure
Found a security issue? Please don’t use the issue tracker but contact us directly. See [SECURITY.md](../SECURITY.md) for details.

## Custom development & contributing code
If you want to contribute to Objectiv or use it as a base for custom development, take a look at [CONTRIBUTING.md](CONTRIBUTING.md). It contains detailed development instructions and a link to information about our contribution process and where you can fit in.

## License
This repository is part of the source code for Objectiv, which is released under the Apache 2.0 License. Please refer to [LICENSE.md](../LICENSE.md) for details.
