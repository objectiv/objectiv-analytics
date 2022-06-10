# Checklock Holmes - Notebook Inspector

**checklock_holmes** is an internal tool we use for checking all modelhub notebooks by creating a script based on
all code-cells and run them against multiple engines.


## How to use

### Requirements

Before start running any checks, please make sure you have all requirements installed. For this just run:

```bash
make requirements
```

In case you want to test with local bach and modelhub code, run:

```bash
make requirements-env
```

### Environment Variables

After installing requirements, make sure you have set up an `.env` file.

For example:
```text
# POSTGRES
PG_DB__DSN=

# BIGQUERY
BQ_DB__DSN=
BQ_DB__CREDENTIALS_PATH=


# METABASE
METABASE_URL = "http://objectiv_metabase:3000"
METABASE_WEB_URL = "http://localhost:3000"
METABASE_USERNAME = "demo@objectiv.io"
METABASE_PASSWORD = "metabase1"
METABASE_DASHBOARD_ID = '1' # 1-model-hub
METABASE_DATABASE_ID = '2' # objectiv database
METABASE_COLLECTION_ID = '2' # 2-object
```
This way, the checker can tell each notebook which engine to use.

### Running Checks

Now that you have everything ready for checks, you can start running the cli-tool.

If you want to know how to use it, just run:

```bash
python checklock-holmes.py --help
```

This will show all supported options:
* `-e` or `--engine`: The engine the checker will use for running the notebooks, by default all engines are considered.
  If you just want to run for specific engines, just provide any of the following options:
  * postgres
  * bigquery

* `--nb`: The notebooks you want to check. By default, it will check all notebooks in `../notebooks` directory
* `--gh_issues_dir`: If any failure was encountered while running the scripts, the checker will write all issues into 
   a markdown file and write in on the provided directory. By default it will write into `github_nb_issues` directory.
* `--dump_nb_scripts_dir`: Directory where to write the scripts ran by the checker, will only store if value is provided

#### Examples

1. Running checks only for bigquery

```bash
python checklock-holmes.py --engine bigquery
```

```bash
python checklock-holmes.py -e bigquery
```

2. Running checks only for multiple engines

```bash
python checklock-holmes.py -e bigquery -e postgres
```

3. Running checks for bigquery and specific notebooks

```bash
python checklock-holmes.py -e bigquery --nb ../notebooks/basic-user-intent.ipynb --nb ../notebooks/basic-product-analytics.ipynb
```

4. Running checks and storing notebook scripts

```bash
python checklock-holmes.py --dump_nb_scripts_dir=.notebook_scripts
```

5. Running checks and stop on the first failed check
```bash
python checklock-holmes.py -x 
```
