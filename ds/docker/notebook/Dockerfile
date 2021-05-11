FROM jupyter/datascience-notebook

RUN pip install psycopg2-binary sqlalchemy && \
    conda update -n base conda && \
    conda install psycopg2  sqlalchemy

# Include an example notebook, in a directory that's not mapped to a volume.
COPY docker/notebook/default_notebook.ipynb /home/jovyan/example_read_only/
