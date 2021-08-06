import React, { CSSProperties } from 'react';
import BoxComponent from './BoxComponent';
import ButtonComponent from './ButtonComponent';
import CircleComponent from "./CircleComponent";
import detectPosition from './detectPosition';
import { ElementContext } from './ElementContext';
import RoundedBoxComponent from "./RoundedBoxComponent";
import ThirdPartyComponent from "./ThirdPartyComponent";
import { trackButton, trackDiv, trackHeader } from './tracker';
import { useElementContext } from './TrackerElementContextProvider';

const appStyle: CSSProperties = {
  padding: 20,
  backgroundColor: 'palegreen',
  zoom: 1.3,
};

const headerStyle: CSSProperties = {
  paddingBottom: 20,
  position: 'fixed',
  top: 35,
  left: '22%'
};

const mainStyle: CSSProperties = {
  display: 'inline',
  verticalAlign: 'top',
};

function App() {
  const { setElementContext } = useElementContext();

  return (
    <>
      <div {...trackDiv('app')} style={appStyle}>
        <h1 style={{ margin: 0, marginBottom: 20 }}>
          App component
          <div style={{ fontSize: '50%', float: 'right', color: 'red' }}>v0.2-epic</div>
        </h1>
        <header {...trackHeader('header')} style={headerStyle}>
          <ButtonComponent id='button-component-1'>Button Component</ButtonComponent>{' '}
          <button
            {...trackButton('inline-button')}
            onClick={async ({ target }) => {
              if (!target || !(target instanceof HTMLElement)) {
                return;
              }
              const elementId = target.dataset.objectiv;
              if (!elementId) {
                return;
              }
              const position = await detectPosition(elementId);
              setElementContext(position);
            }}
          >
            &lt;button&gt; Tag
          </button>
        </header>
        <main style={mainStyle}>
          <div style={{display:'inline-flex', flexDirection: 'column'}}>
            <BoxComponent id="box1" color="mediumpurple" />
            <RoundedBoxComponent id="rounded-box1" color="olive" />
          </div>
          <BoxComponent id="box3" color="cyan">
            <BoxComponent id="box4" color="pink" />
          </BoxComponent>
          <BoxComponent id="box2" color="orange">
            <RoundedBoxComponent id="rounded-box2" color="cadetblue" />
          </BoxComponent>
          <div style={{display:'inline-flex', flexDirection: 'column'}}>
            <CircleComponent id="circle1" color="magenta" />
            <ThirdPartyComponent {...trackDiv('3rd-party')} button1={
              <ButtonComponent id='button-component-2'>Button Component</ButtonComponent>
            }
            button2={
              <button
                {...trackButton('inline-button')}
                onClick={async ({ target }) => {
                  if (!target || !(target instanceof HTMLElement)) {
                    return;
                  }
                  const elementId = target.dataset.objectiv;
                  if (!elementId) {
                    return;
                  }
                  const position = await detectPosition(elementId);
                  setElementContext(position);
                }}
              >
                &lt;button&gt; Tag
              </button>
            }/>
          </div>
          <RoundedBoxComponent id="rounded-box3" color="salmon">
            <CircleComponent id="circle2" color="lightyellow" />
          </RoundedBoxComponent>
        </main>
      </div>
      <ElementContext />
    </>
  );
}

export default App;
