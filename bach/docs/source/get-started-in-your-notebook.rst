.. _get_started_in_your_notebook:

.. frontmatterposition:: 2

.. currentmodule:: modelhub

============================
Get started in your notebook
============================

You can run Objectiv in your favorite notebook, from a self-hosted/local Jupyter notebook to the cloud with 
`Google Colab <https://colab.research.google.com/>`_, `Hex <https://hex.tech/>`_ and 
`Deepnote <https://deepnote.com>`_. See the instructions below.

Jupyter
-------

\1. Install the open model hub locally:

.. code-block:: console

	pip install objectiv-modelhub

\2. Import the required packages in the beginning of your notebook:

.. code-block:: python

	from modelhub import ModelHub

\3. Instantiate the :class:`ModelHub <ModelHub>` and set the default time aggregation:

.. code-block:: python

	modelhub = ModelHub(time_aggregation='%Y-%m-%d')

\4. [See the section below on how to set up the database connection](#set-up-your-database-connection).


Google Colab / Hex / Deepnote
-----------------------------

.. note:: 
    **For Deepnote only:** as a very first step, create a requirements.txt file, add `pandas==1.4.1` to it, 
    and restart the machine.


\1. Install the open model hub in the beginning of your notebook:

.. code-block:: python

	pip install objectiv-modelhub

\2. Import the required packages:

.. code-block:: python

	from modelhub import ModelHub

\3. Instantiate the :class:`ModelHub <ModelHub>` and set the default time aggregation:

.. code-block:: python

	modelhub = ModelHub(time_aggregation='%Y-%m-%d')

\4. Optionally: create an SSH tunnel to the Postgres database server:

.. code-block:: python
	
    pip install sshtunnel

.. code-block:: python

    from sshtunnel import SSHTunnelForwarder
    import os, stat

    # SSH tunnel configuration
    ssh_host = ''
    ssh_port = 22
    ssh_username = ''
    ssh_passphrase = ''
    ssh_private_key= ''
    db_host = ''
    db_port = 5432

    try:
        pk_path = '._super_s3cret_pk1'
        with open(pk_path, 'a') as pkf:
            pkf.write(ssh_private_key)
            os.chmod(pk_path, stat.S_IREAD)

        ssh_tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_username,
            ssh_private_key=pk_path,
            ssh_private_key_password=ssh_passphrase,
            remote_bind_address=(db_host, db_port)
        )
        ssh_tunnel.start()
        os.remove(pk_path)
        tunnel_port = ssh_tunnel.local_bind_port

    except Exception as e:
        os.remove(pk_path)
        raise(e)

\5. [See the section below on how to set up the database connection](#set-up-your-database-connection).


Set up your database connection
-------------------------------

Now we can connect to the database, and create an Objectiv :class:`DataFrame <bach.DataFrame>`. This 
DataFrame then points to the data in the database, and all operations are done directly on it.

.. note:: 
    When setting up the database connection and creating the Objectiv DataFrame, you can pass multiple 
    parameters (such as `start_date` and `end_date` above). See the 
    :py:meth:`get_objectiv_dataframe <ModelHub.get_objectiv_dataframe>` call for details.

**PostgreSQL - without a tunnel**:

.. code-block:: python

    df = modelhub.get_objectiv_dataframe(
      db_url='postgresql://USER:PASSWORD@HOST:PORT/DATABASE',
      start_date='2022-06-01',
      end_date='2022-06-30',
      table_name='data')


**PostgreSQL - with a tunnel**:

.. code-block:: python

    df = modelhub.get_objectiv_dataframe(
        db_url=f'postgresql://USER:PASSWORD@localhost:{tunnel_port}/DATABASE',
        start_date='2022-06-01',
        end_date='2022-06-30',
        table_name='data')

**Google BigQuery**

Google BigQuery is supported via a Snowplow pipeline. See `how to set up GCP & BigQuery 
</docs/tracking/backend/snowplow/gcp-and-bigquery>`_.

With `BQ_CREDENTIALS_PATH` the path to the credentials for your BigQuery connection, e.g. 
`/home/myusername/myrepo/.secrets/production--bigquery.json`:

.. code-block:: python

    df = modelhub.get_objectiv_dataframe(
        db_url='USER://DATABASE/snowplow',
        start_date='2022-06-01', 
        end_date='2022-06-30',
        table_name='events',
        bq_credentials_path=BQ_CREDENTIALS_PATH)


Next steps
----------

After the steps above, you're ready to go! 

Check out the :doc:`example notebooks <./example-notebooks/index>` and the 
:doc:`open model hub <open-model-hub/index>` for what to do next.
