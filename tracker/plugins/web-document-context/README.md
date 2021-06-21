# Objectiv WebDocumentContext Plugin
Detects the current URL via the document's [Location API](https://developer.mozilla.org/en-US/docs/Web/API/Location/href) and factors a `WebDocumentContext` that is attached to each `TrackerEvent`'s `global_contexts` during their `beforeTransport` phase.

Listens to [History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API) state changes and automatically triggers `URLChangedEvent`s.

Listens to [DOMContentLoaded](https://developer.mozilla.org/en-US/docs/Web/API/Window/DOMContentLoaded_event) and automatically triggers `DocumentLoadedEvent`s.

### Configuration

| Option              | Type Required | Required | Default value                         |
| ------------------- | ------------- | -------- | ------------------------------------- |
| `documentContextId` | `string`      | No       | The document node id. Eg. `#document` |

### WebDocumentContext

```typescript
{
  _context_type: 'WebDocumentContext';
  id: string;
  url: string; 
};
```

### URLChangedEvent

```typescript
{
  event: 'URLChangedEvent';
  location_stack: [
    {
      _context_type: 'WebDocumentContext',
      id: string,
      url: string,
    }   
  ]
};
```

### DocumentLoadedEvent

```typescript
{
  event: 'DocumentLoadedEvent';
  location_stack: [
    {
      _context_type: 'WebDocumentContext',
      id: string,
      url: string,
    }   
  ]
};
```

---
# Installing
To install the most recent stable version:

### yarn
```sh
yarn add @objectiv/plugin-web-document-context
```

### npm
```sh
npm install @objectiv/plugin-web-document-context
```

# Usage
[PLACEHOLDER: Refer to DOCS on how to initialize / extend Tracker Plugins]
