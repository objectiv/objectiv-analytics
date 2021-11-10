# Objectiv WebDocumentContext Plugin

[![License][license-badge]][license-url] [![Coverage][coverage-badge]](#)

Plugin for Objectiv web trackers. Detects the current URL via the document's Location API and factors in a `WebDocumentContext` that is attached to each `TrackerEvent`'s `global_contexts` before transport. Also listens to DOMContentLoaded to automatically trigger `DocumentLoadedEvent`s.

---
## Package Installation
To install the most recent stable version:

```sh
yarn add @objectiv-analytics/plugin-web-document-context
```

### or
```sh
npm install @objectiv-analytics/plugin-web-document-context
```

# Usage
For a detailed usage guide, see the documentation: [https://objectiv.io/docs](https://objectiv.io/docs)

# Copyright and license
Licensed and distributed under the Apache 2.0 License (An OSI Approved License).

Copyright (c) 2021 Objectiv B.V.

All rights reserved.

[license-badge]: https://img.shields.io/badge/license-Apache--2.0-blue.svg
[license-url]: https://www.apache.org/licenses/LICENSE-2.0
[coverage-badge]: https://img.shields.io/badge/Coverage-100%25-brightgreen.svg
