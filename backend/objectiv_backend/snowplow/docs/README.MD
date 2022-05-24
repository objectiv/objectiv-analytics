# Snowplow pipeline support

The Objectiv collector supports using the Snowplow pipeline as a sink for Objectiv events. Currently, there is support 
for Google PubSub and AWS SQS/Kinesis, using Thrift messages. This means we by-pass the Snowplow collector, but hook 
directly into Snowplows enrichment step.

## Architecture
The Snowplow pipeline roughly consists of the following components:
1. `Collector` - http(s) endpoint that receives events
2. `Enrichment` - process that validates incoming events, potentially enriches them (adds metadata)
3. `Loader` - final step, where the validated and enriched events are loaded into persistent storage. Depending on your 
  choice of platform, this could be Big Query on GCP, Redshift on AWS, etc
4. `iglu` - central repository, used by other components to pull schema to do validation on events, contexts, etc.
The Snowplow pipeline uses message queues and Thrift messages to communicate between the components.

Objectiv uses its own collector (which also handles validation), so bypasses the Snowplow collector, but pushes events 
directly into the message queue that is read by the `enrichment`. Snowplow allows for so-called structured custom 
contexts to be added to events. This is exactly what Objectiv uses. As with all contexts, they must pass validation in 
the enrichment step, which is why a schema for the Objectiv custom context must be added to iglu.

This way Snowplow knows how to validate the context. Furthermore, it also infers the database schema to be able to persist
the context. How this is handled depends on the loader chosen (e.g. Postgres uses a different, more relational schema 
than for instance Big Query).

## Setup
In this setup, we assume you already have a fully functional Snowplow pipeline running, including enrichment, loader 
and iglu repository. If you haven't, the [Snowplow quickstart for Open Source](https://docs.snowplowanalytics.com/docs/open-source-quick-start/what-is-the-quick-start-for-open-source/) is a good place to start. 

Enabling Objectiv involves two steps:
1. Add the Objectiv Taxonomy schema to the iglu repository.
2. Configure the Objectiv Collector output to push events into the appropriate message queue.

### Add the Objectiv schema to the iglu repo
This explains how to get the Objectiv schema into iglu. This is necessary, so the Snowplow pipeline (enrichment) can 
validate the incoming custom contexts.
#### Preparation

- copy the Objectiv iglu schema (see [1-0-0](1-0-0) in this dir) into `schemas/io.objectiv/taxonomy/jsonschema/1-0-0` in your local repo
- get the address / URL of your iglu repository
- get the uuid of the repo

#### Pushing the schema
```shell
java -jar igluctl static push --public <path to schemas> <url to repo> <uuid>

## example:
java -jar igluctl static push --public ./schemas https://iglu.example.com myuuid-abcd-abcd-abcd-abcdef12345
``` 


### Enabling the collector output
The collector can be configured to push events into a Snowplow message queue, using environment 
variables. Please refer to [aws.md](aws.md) or [gcp.md](gcp.md) for the platform specific instructions.



# Maintenance

## Thrift schema
Compiling the Thrift schema into Python (should normally not be needed). The schema looks like this:
```java
namespace java com.snowplowanalytics.snowplow.CollectorPayload.thrift.model1

struct CollectorPayload {
  31337: string schema

  // Required fields which are intrinsic properties of HTTP
  100: string ipAddress

  // Required fields which are Snowplow-specific
  200: i64 timestamp
  210: string encoding
  220: string collector

  // Optional fields which are intrinsic properties of HTTP
  300: optional string userAgent
  310: optional string refererUri
  320: optional string path
  330: optional string querystring
  340: optional string body
  350: optional list<string> headers
  360: optional string contentType

  // Optional fields which are Snowplow-specific
  400: optional string hostname
  410: optional string networkUserId
}
```
source: https://github.com/snowplow/snowplow/blob/master/2-collectors/thrift-schemas/collector-payload-1/src/main/thrift/collector-payload.thrift

The Python code can then be generated using:
```shell
  curl https://raw.githubusercontent.com/snowplow/snowplow/master/2-collectors/thrift-schemas/collector-payload-1/src/main/thrift/collector-payload.thrift
  thrift --gen py  collector-payload.thrift
```
This will create a dir `gen-py/schema/`, containing `constants.py` and `ttypes.py`. These need to be copied into 
`backend/objeciv_bach/snowplow/schema`.
