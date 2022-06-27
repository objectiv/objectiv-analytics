<img src="https://user-images.githubusercontent.com/82152911/159266790-19e0e3d4-0d10-4c58-9da7-16edde9ec05a.svg#gh-light-mode-only" alt="objectiv_logo_light" title="Objectiv Logo">
<img src="https://user-images.githubusercontent.com/82152911/159266895-39f52604-83c1-438d-96bd-9a6d66e74b08.svg#gh-dark-mode-only" alt="objectiv_logo_dark" title="Objectiv Logo">

[Objectiv](https://objectiv.io/) is open-source product analytics infrastructure, built around a [generic taxonomy](https://www.objectiv.io/docs/taxonomy).

* Collect validated user behavior data with an event structure designed for modeling
* Send it into your SQL datastore of choice without stopovers
* Model on the raw data without cleaning & transformation 
* Build models on one dataset, deploy and run them on another 
* Use pandas-like operations that run on the full SQL dataset
* Stack pre-built models and functions to build in-depth analyses quickly
* Convert models to SQL to feed dashboards, BI tools, pipelines etc. from one source

Self-hosted, 100% free to use and fully open source.

### Demo

Follow our [Quickstart Guide](https://objectiv.io/docs/home/quickstart-guide) to set up a fully functional dockerized demo in under 5 minutes.

### Resources

* [Objectiv Docs](https://www.objectiv.io/docs) - Objectiv's official documentation.
* [Objectiv on Slack](https://objectiv.io/join-slack) - Get help & join the discussion on where to take Objectiv next.
* [Objectiv.io](https://www.objectiv.io) - Objectiv's official website.

---

## What's in the box?
![objectiv_stack](https://user-images.githubusercontent.com/82152911/161998050-7ec9e452-20c7-447f-a61f-12b904733c74.svg#gh-light-mode-only "Objectiv Stack")
![objectiv_stack_dark](https://user-images.githubusercontent.com/82152911/161998028-4dbe0759-fb8d-4579-b2c9-200e69adc821.svg#gh-dark-mode-only "Objectiv Stack")


### Open analytics taxonomy

Enables a [generic way to collect & structure rich analytics events](https://www.objectiv.io/docs/taxonomy). Describes classes for common user interactions and their contexts. 

[![taxonomy](https://user-images.githubusercontent.com/82152911/162000133-1eea0192-c882-4121-a866-8c1a3f8ffee3.svg)](https://www.objectiv.io/docs/taxonomy)

* Used for data validation and debugging of instrumentation
* Designed to ensure collected data is model-ready without cleaning, transformation or tracking plans
* Results in consistent data: models can be shared/reused between teams, products & (data)platforms

Supports a wide range of product analytics use cases. We're currently working on extending the range of marketing related use cases.

### Tracking SDK

Supports front-end engineers to [implement tracking instrumentation](https://www.objectiv.io/docs/tracking) that embraces the open analytics taxonomy.

* Provides guidance, validation & E2E esting to help setting up error-free instrumentation
* Support for React, React Native, Angular and Browser
 
### Open model hub

A [growing collection of pre-built models and functions](https://objectiv.io/docs/modeling/open-model-hub/) to run, combine or customize for quick, in-depth analyses.

* Covers a wide range of use cases: from basic product analytics to predictive analysis with ML
* Works with any dataset that embraces the open analytics taxonomy
* New models & functions are added continuously (coming up: impact attribution of product features on conversion)

### Bach modeling library

Python-based [modeling library](https://www.objectiv.io/docs/modeling/bach/) that enables using pandas-like operations on the full SQL dataset.

* Includes specific operations to easily work with data sets that embrace the open analytics taxonomy
* Pandas-compatible: use popular pandas ML libraries in your models
* Output your entire model to SQL with a single command

---

## Compatible data stores

Objectiv currently supports PostgreSQL. We're working on support for Snowplow and BigQuery for event handling at scale. Amazon Redshift is planned next.

---

For more information, visit [objectiv.io](https://www.objectiv.io) or [Objectiv Docs](https://www.objectiv.io/docs) - Objectiv's official documentation..

---

This repository is part of the source code for Objectiv, which is released under the Apache 2.0 License. Please refer to [LICENSE.md](LICENSE.md) for details.
