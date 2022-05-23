# Objectiv Backend

Running the backend will enable you to receive and process tracking data in your environment. It consists of three images:

* `objectiv_collector` - Endpoint that the Objectiv-tracker can send events to (http://localhost:5000).
* `objectiv_postgres` - Database to store data.
* `objectiv_notebook` - Jupyter notebook that can be used to query the data (http://localhost:8888).

## Running the Backend Dockerized
The below commands assume that you have `docker-compose` [installed](https://docs.docker.com/compose/install/).
```bash
docker-compose pull  # pull pre-built images from gcr
docker-compose up    # spin up Objective pipeline
```
SECURITY WARNING: The above docker-compose commands start a postgres container that allows connections
without verifying passwords. Do not use this in production or on a shared system!

For detailed installation & usage instructions, visit [Objectiv Docs](https://www.objectiv.io/docs/tracking/collector).

## Support & Troubleshooting
If you need help using or installing Objectiv, join our [Slack channel](https://objectiv.io/join-slack/) and post your question there. 

## Bug Reports & Feature Requests
If you’ve found an issue or have a feature request, please check out the [Contribution Guide](https://objectiv.io/docs/home/the-project/contribute/).

## Security Disclosure
Found a security issue? Please don’t use the issue tracker but contact us directly. See [SECURITY.md](../SECURITY.md) for details.

## Custom Development & Contributing Code
If you want to contribute to Objectiv or use it as a base for custom development, take a look at [CONTRIBUTING.md](CONTRIBUTING.md). It contains detailed development instructions and a link to information about our contribution process and where you can fit in.

## License
This repository is part of the source code for Objectiv, which is released under the Apache 2.0 License. Please refer to [LICENSE.md](../LICENSE.md) for details.
