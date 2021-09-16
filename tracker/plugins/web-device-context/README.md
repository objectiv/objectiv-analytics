# Objectiv WebDeviceContext Plugin
Detects the user agent string for the current browser via the [Navigator API](https://developer.mozilla.org/en-US/docs/Web/API/NavigatorID/userAgent), during its instantiation, to factor a `WebDeviceContext`.  

The Context is then attached to each `TrackerEvent`'s `global_contexts` during its `beforeTransport` phase.  

### WebDeviceContext
```typescript
{
  _type: 'WebDeviceContext';
  id: 'device';
  user_agent: string;               
}
```

---

# Installing
To install the most recent stable version:

### yarn
```sh
yarn add @objectiv/plugin-web-device-context
```

### npm
```sh
npm install @objectiv/plugin-web-device-context
```

# Usage
[PLACEHOLDER: Refer to DOCS on how to initialize / extend Tracker Plugins]
