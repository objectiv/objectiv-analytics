import React, { CSSProperties } from 'react';
import Box from './Box';
import Button from './Button';
import detectPosition from './detectPosition';
import { ElementContext } from './ElementContext';
import { tracker } from './tracker';
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
      <tracker.div id="app" style={appStyle}>
        <h1 style={{ margin: 0, marginBottom: 20 }}>App component</h1>
        <tracker.header id="header" style={headerStyle}>
          <Button>Button Component</Button>{' '}
          <tracker.button
            id="inline-button"
            onClick={async () => {
              const position = await detectPosition('');
              setElementContext(position);
            }}
          >
            &lt;button&gt; Tag
          </tracker.button>
        </tracker.header>
        <main style={mainStyle}>
          <Box color="mediumpurple" />
          <Box color="orange" />
          <Box color="lightblue">
            <Box color="lavender" />
          </Box>
          <Box color="salmon" />
        </main>
      </tracker.div>
      <ElementContext />
    </>
  );
}

export default App;
