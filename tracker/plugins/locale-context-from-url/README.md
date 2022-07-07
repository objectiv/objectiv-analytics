# Objectiv LocaleContextFromURL Plugin

Plugin for Objectiv web trackers. Detects the locale by applying a RegExp to the current URL, via the document's Location API, and factors in a `LocaleContext` that is attached to each `TrackerEvent`'s `global_contexts` before transport.

---
## Package Installation
To install the most recent stable version:

```sh
yarn add @objectiv/plugin-locale-context-from-url
```

### or
```sh
npm install @objectiv/plugin-locale-context-from-url
```

# Usage
For a detailed usage guide, see the documentation: [https://objectiv.io/docs](https://objectiv.io/docs)

# Copyright and license
Licensed and distributed under the Apache 2.0 License (An OSI Approved License).

Copyright (c) 2022 Objectiv B.V.

All rights reserved.
