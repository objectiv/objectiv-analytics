import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { TrackerElementContextProvider } from './TrackerElementContextProvider';

ReactDOM.render(
  <React.StrictMode>
    <TrackerElementContextProvider>
      <App />
    </TrackerElementContextProvider>
  </React.StrictMode>,
  document.getElementById('root')
);
