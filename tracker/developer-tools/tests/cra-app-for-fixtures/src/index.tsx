import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { PositionContextProvider } from "./PositionProvider";

ReactDOM.render(
  <React.StrictMode>
    <PositionContextProvider>
      <App />
    </PositionContextProvider>
  </React.StrictMode>,
  document.getElementById('root')
);
