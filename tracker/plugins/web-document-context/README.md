# Objectiv WebDocumentContext Plugin

Plugin for Objectiv web trackers. Detects the current URL via the document's Location API and factors in a `WebDocumentContext` that is attached to each `TrackerEvent`'s `global_contexts` before transport. Also listens to DOMContentLoaded to automatically trigger `DocumentLoadedEvent`s.

---
## Package Installation
To install the most recent stable version:

```sh
yarn add @objectiv/plugin-web-document-context
```

### or
```sh
npm install @objectiv/plugin-web-document-context
```

# Usage
For a detailed usage guide, see the documentation: [https://objectiv.io/docs](https://objectiv.io/docs)

# Copyright and license
Licensed and distributed under the Apache 2.0 License (An OSI Approved License).

Copyright (c) 2021 Objectiv B.V.

All rights reserved.
