import React, { CSSProperties } from 'react';
import Box from './Box';
import Button from './Button';
import detectPosition from './detectPosition';
import { ElementContext } from './ElementContext';
import { trackButton, trackDiv, trackHeader } from './tracker';
import { useElementContext } from './TrackerElementContextProvider';

const appStyle: CSSProperties = {
  padding: 20,
  backgroundColor: 'lightgreen',
};

const headerStyle: CSSProperties = {
  paddingBottom: 20,
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
        <h1 style={{ margin: 0, marginBottom: 20 }}>App component</h1>
        <header {...trackHeader('header')} style={headerStyle}>
          <Button>Button Component</Button>{' '}
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
          <Box id="purple" color="mediumpurple" />
          <Box id="orange" color="orange" />
          <Box id="cyan" color="cyan">
            <Box id="pink" color="pink" />
          </Box>
          <Box id="green" color="brown" />
        </main>
      </div>
      <ElementContext />
    </>
  );
}

export default App;
