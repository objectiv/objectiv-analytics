import React, { createRef, CSSProperties } from 'react';
import BoxComponent from './BoxComponent';
import ButtonComponent from './ButtonComponent';
import CircleComponent from './CircleComponent';
import detectPosition from './detectPosition';
import { ElementContext } from './ElementContext';
import RoundedBoxComponent from './RoundedBoxComponent';
import ThickBoxComponent from './ThickBoxComponent';
import ThirdPartyComponent from './ThirdPartyComponent';
import { trackButton, trackElement } from './tracker';
import { useElementContext } from './TrackerElementContextProvider';

const appStyle: CSSProperties = {
  padding: 20,
  backgroundColor: 'palegreen',
  zoom: 1.3,
  overflow: 'scroll',
};

const headerStyle: CSSProperties = {
  paddingBottom: 20,
  position: 'absolute',
  top: 35,
  left: '22%',
};

const mainStyle: CSSProperties = {
  display: 'inline',
  verticalAlign: 'top',
};

function App() {
  const { setElementContext } = useElementContext();

  const boxComponentRef = createRef<HTMLDivElement>();
  const BoxComponentWithForwardedRef = React.forwardRef<HTMLDivElement, { id: string; color: string }>((props, ref) => (
    <BoxComponent {...props} forwardedRef={ref} />
  ));

  return (
    <>
      <div {...trackElement('app')} style={appStyle}>
        <h1 style={{ margin: 0, marginBottom: 20 }}>
          App component
          <div style={{ fontSize: '50%', float: 'right', color: 'red' }}>v0.2-epic</div>
        </h1>
        <header {...trackElement('header')} style={headerStyle}>
          <ButtonComponent id="button-component">Button Component</ButtonComponent>{' '}
          <button
            {...trackButton('inline-button')}
            onClick={async ({ target }) => {
              const position = await detectPosition(target);
              setElementContext(position);
            }}
          >
            &lt;button&gt; Tag
          </button>
        </header>
        <main style={mainStyle}>
          <div style={{ display: 'inline-flex', flexDirection: 'column' }}>
            <BoxComponent id="box1" color="mediumpurple" />
            <RoundedBoxComponent id="rounded-box1" color="olive" />
          </div>
          <BoxComponent id="box2" color="cyan">
            <BoxComponent id="box4" color="pink" />
          </BoxComponent>
          <BoxComponent id="box3" color="orange">
            <RoundedBoxComponent id="rounded-box2" color="cadetblue" />
          </BoxComponent>
          <div style={{ display: 'inline-flex', flexDirection: 'column' }}>
            <CircleComponent id="circle1" color="lightblue" />
            <ThirdPartyComponent
              {...trackElement('3rd-party')}
              button1={<ButtonComponent id="button-component-2">Button Component</ButtonComponent>}
              button2={
                <button
                  {...trackButton('inline-button')}
                  onClick={async ({ target }) => {
                    const position = await detectPosition(target);
                    setElementContext(position);
                  }}
                >
                  &lt;button&gt; Tag
                </button>
              }
            />
          </div>
          <RoundedBoxComponent id="rounded-box3" color="salmon">
            <CircleComponent id="circle2" color="lightyellow" />
          </RoundedBoxComponent>
          <ThickBoxComponent id="thickbox3" color="orange" />
          <BoxComponentWithForwardedRef ref={boxComponentRef} id="wrapped-box" color="red" />
        </main>
      </div>
      <ElementContext onClick={() => setElementContext({})} />
    </>
  );
}

export default App;
