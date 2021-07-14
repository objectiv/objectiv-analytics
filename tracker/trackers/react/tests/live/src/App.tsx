import { makeLinkContext, trackLinkClick, useTrackApplicationLoaded, useTracker } from "@objectiv/tracker-react";
import logo from './logo-objectiv.svg';
import './App.css';

function App() {
  const tracker = useTracker();

  useTrackApplicationLoaded();

  return (
    <>
      <header className="header">
        <a className="link" href="/">
          <div className="logo-wrapper">
            <img src={logo} className="logo-image" alt="Objectiv" />
          </div>
        </a>
      </header>

      <div className="layout">
        <div className="sidebar">

          <ul className="menu">
            <li className="menu-item menu-item-active"><a href="/guide/introduction">Introduction</a></li>
            <li className="menu-item"><a href="/guide/get-started">Get Started</a></li>
            <li className="menu-item"><a href="/guide/use-with-create-react-app">Use in create-react-app</a></li>
          </ul>

        </div>
        <div className="body">
          body
          <div
            onClick={
              () => trackLinkClick(makeLinkContext({id: 'test-link', href: '/', text: 'Track Link Click'}), tracker)
            }>
            Track Link Click
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
