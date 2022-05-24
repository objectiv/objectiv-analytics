import { ObjectivProvider, ReactTracker } from "@objectiv/tracker-react";
import { DebugTransport } from "@objectiv/transport-debug";
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

require('@objectiv/developer-tools');

const tracker = new ReactTracker({
  applicationId: 'e2e-react-cra',
  transport: new DebugTransport()
})

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <ObjectivProvider tracker={tracker}>
    <React.StrictMode>
      <App />
    </React.StrictMode>
  </ObjectivProvider>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
