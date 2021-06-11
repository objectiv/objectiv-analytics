# Objectiv JavaScript Tracker Core 
[PLACEHOLDER: Objectiv JavaScript Tracker Core introductory text]

---
# Installing
To install the most recent stable version:

### yarn
```sh
yarn add @objectiv/tracker-core
```

### npm
```sh
npm install @objectiv/tracker-core
```

# Usage

### ESModule
```javascript
import { Tracker } from '@objectiv/tracker-core';
const tracker = new Tracker();
```

### CommonJS
```javascript
const objectiv = require('@objectiv/tracker-core');
const tracker = new objectiv.Tracker();
```

### IIFE
```html
<script src="dist/index.iife.js"></script>
<script>
  const tracker = new objectiv.Tracker();
</script>
```

### AMD
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js"></script>
<script>
  window.requirejs(['dist/index'], function(objectiv) {
    const tracker = new objectiv.Tracker();
  });
</script>
```
