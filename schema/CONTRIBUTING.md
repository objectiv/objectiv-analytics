# Open analytics taxonomy - Development

Here you'll find instructions for development on the open analytics taxonomy. If you want to contribute (Thank you!), please take a look at the [Contribution Guide](https://www.objectiv.io/docs/home/the-project/contribute) in our Docs. It contains information about our contribution process and where you can fit in.

## Schema updates

Schema (and extensions) are kept in /schema. The format used, is loosely based on JSON-schema, and used a JSON5 encoding to allow for multiline strings.

The two main schema are:
- the base schema (base_schema.json5). This schema contains definitions of all events, contexts and their hierarchy, that are contained in the base setup. They are used (and validated) across the whole pipeline.
- the event list schema (event_list.json5). This schema contains the definition of the structure of messages between the tracker and the collector. In short, it describes a structure to send a list of events (as defined in the aforementioned base schema).

## Validation
Validation takes place on a few levels:
1. in code (currently there is support for JS/TS and Python)
2. at runtime at reception of events by the collector.

In code this works by code that is generated from the schema. Of course it is very important to keep code and schema in sync. As a safeguard there is a Github Action in place that checkes this.

## Generation
So how does this work?
1. Make any changes to the base schema and/or add extensions
2. Make sure to regenerate both TS and Python definitions
3. Run tests
4. If all is OK, create a PR (in the case of changes to the base schema)

### Tracker: Typescript
For TypeScript, there is a generator.js script in tracker/core/utility/dist/. Using it is quite simple:
```bash
cd tracker && yarn utils:generate
```

### Collector: Python
As for Python the approach is pretty similar:
1. Make sure to properly set up the VirtualEnv, as described in backend/README.md
2. Run the following command:
```bash
cd backend
make base_schema
python3 objectiv_backend/schema/generate_classes.py
autopep8 -i schema.py
mv schema.py objectiv_backend/schema
make tests
```

