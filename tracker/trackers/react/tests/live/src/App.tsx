import logo from './logo-objectiv.svg';
import './App.css';
import MenuItem from "./MenuItem";
import { BrowserRouter, Switch, Route } from "react-router-dom";

// @ts-ignore .tsx is not allowed in imports but we have a preloader in place to support it
import cases from "./cases/**/*.tsx";

export type Case = {
  urlSlug: string,
  menuLabel: string,
  Component: any
}

function App() {
  return (
    <BrowserRouter>
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
            {cases.map((props: Case, index: number) => <MenuItem key={index} {...props} />)}
          </ul>

        </div>
        <div className="body">
          <Switch>
            {cases.map(({ Component, urlSlug }: Case, index: number) => (
              <Route key={index} path={`/${urlSlug}`} exact={true} component={Component} />
            ))}
          </Switch>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
