# Configuring the Objectiv Collector to work with GCP
The Objectiv Collector can be configured to work with Snowplow on GCP. The Snowplow GCP setup uses GCP PubSub topics 
(message queue) to connect various stages in the pipeline. The setup works as follows:
- Events arrive at the Objectiv Collector, and are validated.
- Good events are published on the `raw` topic on PubSub (which is read by the Enrich process)
- Bad events (invalid) are published on the `bad` topic on PubSub.

Before starting up the Objectiv Collector, some preparation is required. The following sections assume there's already
a running and functional Snowplow pipeline setup on GCP. If you don't, Snowplow has a 
[quick start installation guide](https://docs.snowplowanalytics.com/docs/open-source-quick-start/quick-start-installation-guide-on-gcp/)
to get you up and running.

#### Starting the collector
The configuration for the collector is controlled through environment variables. They allow you to configure which outputs
will be used. Settings specific to the PubSub sin are:

- `SP_GCP_PROJECT` This is the `id` of the project on GCP where the PubSub topic is located
- `SP_GCP_PUBSUB_TOPIC_RAW` This is the `id` of the PubSub topic to publish events to
- `SP_GCP_PUBSUB_TOPIC_BAD` This is the `id` of the PubSub topic to publish bad/invalid events to
- `GOOGLE_APPLICATION_CREDENTIALS` This is the path to a `json` containing a service account on GCP that allows publishing
 to the PubSub topic.

If these are set, the snowplow sink is automatically enabled.

#### Using docker-compose
To run this setup in docker, make sure that the aforementioned environment variables are properly set and available in the
container. Also take care that the path to the credentials is actually available in the container.

When using `docker-compose`, the following yaml snippet would do the trick:
```yaml
  objectiv_collector:
    container_name: objectiv_collector
    image: objectiv/backend
    working_dir: /services
    ports:
      - "127.0.0.1:5000:5000"
    volumes:
      - /path/to/YOUR_SERVICE_ACCOUNT.json:/sa.json
    environment:
      SP_GCP_PROJECT: some-gcp-project
      SP_GCP_PUBSUB_TOPIC_RAW: sp-raw
      SP_GCP_PUBSUB_TOPIC_BAD: sp-bad
      GOOGLE_APPLICATION_CREDENTIALS: /sa.json
      OUTPUT_ENABLE_PG: false
```

The important parts here are:
- using a volume to make the service account available inside the container
- assigning the path of the volume-mapped file correctly to the environment variable
- setting the 2 GCP/PubSub variables, to make sure the collector knows where to push the events to

#### Running locally
Running the collector locally, in a dev setup is pretty similar:

```sh
# setup environment
virtualenv objectiv-venv
source objectiv-venv/bin/activate
pip install -r requirements.in

# start flask app
cd objectiv_backend
export PYTHONPATH=.:$PYTHONPATH
GOOGLE_APPLICATION_CREDENTIALS=/path/to/YOUR_SERVICE_ACCOUNT.json \
 SP_GCP_PROJECT=some-gcp-project \
 SP_GCP_PUBSUB_TOPIC_RAW=sp-raw \
 SP_GCP_PUBSUB_TOPIC_BAD=sp-bad \
 flask run
```

## Testing
The collector will display a message if the Snowplow config is loaded:
`Enabled Snowplow: GCP pipeline`.
This indicates that the collector will try to push events. If this fails, logging should hint what's happening. If there 
are no errors in the collector logs, the events should be successfully pushed into the raw topic, to be picked up by 
Snowplow's enrichment.
To check if messages have been successfully received by the PuSub topic, please refer to the monitoring of that specific 
topic in the GCP console. The `Publish message request count` monitoring topic should show more than 0 requests/sec.

## Big Query table
In a standard Snowplow Big Query setup, all data is stored in a table called `events`. As this table holds a lot of data
it contains over 100 columns. Objectiv events will be stored using the schema from iglu, and require just one column
to hold the JSON structure of the event.

If BQ is only used for Objectiv, there are obviously a lot of unused columns, often not even populated. This can be 
solved in a few steps (as it's not possible to simply drop columns from BQ):
1. Stop the Snowplow bigquery streamloader, to make sure we don't lose any data during the migration
2. [optional] Create a backup of the events table
3. [Rename the events table](https://cloud.google.com/bigquery/docs/managing-tables#renaming-table):
```sql
ALTER TABLE `project.snowplow.events`
RENAME TO `project.snowplow.events_copy`
```
 Alternatively (if rename doesn't work):
- Create a copy: `events_copy`
- Drop `events`
4. Query desired columns into new table:
```sql
-- Make sure to add any columns that contain custom contexts here
-- Be very careful here!
CREATE TABLE `project.snowplow.events` 
PARTITION BY date_trunc(load_tstamp, DAY)
AS SELECT app_id, platform, etl_tstamp, collector_tstamp, event, event_id, 
  v_tracker, v_collector, v_etl, user_ipaddress, network_userid, 
  page_url, page_urlscheme, page_urlhost, page_urlport, page_urlpath, page_urlquery, page_urlfragment,
  
  mkt_medium, mkt_source, mkt_term, mkt_content, mkt_campaign, mkt_network, mkt_clickid,
  refr_medium, refr_source, refr_term,
  useragent, 
  derived_tstamp, event_vendor, event_name, event_format, event_version, event_fingerprint,
  load_tstamp
FROM `project.snowplow.events_copy`;
```
5. Restart the Snowplow bigquery streamloader
6. Verify new events end up in the `events` table, and check the failed-inserts PubSub topic
7. Remove `events_copy`