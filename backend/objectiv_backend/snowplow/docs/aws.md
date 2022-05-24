# Configuring the Objectiv Collector to work with AWS
The Objectiv Collector can be configured to work with Snowplow on AWS. The Snowplow AWS setup uses either SQS 
(message queue) or Kinesis to connect various stages in the pipeline. The setup works as follows:
- Events arrive at the Objectiv Collector, and are validated.
- Good events are published on the `raw` topic on Kinesis or SQS (which in turn is processed by Enrich)
- Bad events (invalid) are published on the `bad` topic on Kinesis.

Before starting up the Objectiv Collector, some preparation is required. The following sections assume there's already
a running and functional Snowplow pipeline setup on AWS. If you don't, Snowplow has a 
[quick start installation guide](https://docs.snowplowanalytics.com/docs/open-source-quick-start/quick-start-installation-guide-on-aws/)
to get you up and running.

#### Starting the collector
The output topics of the collector are controlled through environment variables:

- `SP_AWS_MESSAGE_TOPIC_RAW` - this can be either the id of a Kinesis stream (eg. sp-raw-stream) _or_ a URL to an SQS queue (eg. https://sqs.someregion.amazonaws.com/123455/sp-raw-queue)
- `SP_AWS_MESSAGE_TOPIC_BAD` - this should be the id of the Kinesis bad stream (eg. sp-bad-stream)

The AWS integration uses the boto3 python library, this means authentication is also provided through that library 
(As detailed [here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)). 
The simplest way to make it work, is by setting the following environment variables:
- `AWS_ACCESS_KEY_ID` - iAM key of the account used to access AWS services
- `AWS_SECRET_ACCESS_KEY` - iAM secret key
- `AWS_DEFAULT_REGION` - Optionally specify the AWS region in which the Kinesis/SQS resources are deployed.

Once these environment variables have been set, the Objectiv Collector can be started, and the Snowplow AWS output will be enabled.

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
    environment:
      AWS_ACCESS_KEY_ID: AKIA-some-key
      AWS_SECRET_ACCESS_KEY: some-secret-key
      AWS_DEFAULT_REGION: some-aws-region
      SP_AWS_MESSAGE_TOPIC_RAW: sp-raw-stream
      SP_AWS_MESSAGE_TOPIC_BAD: sp-bad-stream
      OUTPUT_ENABLE_PG: false
```

The important part here is setting the correct env:
- providing the AWS credentials
- providing the Kinesis stream ids

#### Running locally
Running the collector locally, in a dev setup is pretty similar:

```sh
# setup environment
virtualenv objectiv-venv
source objectiv-venv/bin/activate
pip install -r requirements.in

# start flask app, using SQS queue
cd objectiv_backend
export PYTHONPATH=.:$PYTHONPATH
SP_AWS_MESSAGE_TOPIC_RAW=sp-raw-stream \
  SP_AWS_MESSAGE_TOPIC_BAD=sp-bad-stream \
  flask run
```

## Testing
The collector will display a message if the Snowplow config is loaded:
`Enabled Snowplow: AWS pipeline ($SP_AWS_MESSAGE_TOPIC)`.
This indicates that the collector will try to push events. If this fails, logging should hint what's happening. If there 
are no errors in the collector logs, the events should be successfully pushed into the raw topic, to be picked up by 
Snowplow's enrichment.
To check if the messages have successfully arrived in the queue, please review to monitoring in the AWS console. Events 
should show up as either `PutRecords` (Kinesis) or `Number of messages received (SQS) 