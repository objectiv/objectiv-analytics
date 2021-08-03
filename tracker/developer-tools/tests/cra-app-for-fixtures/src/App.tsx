import React from 'react';
import Box from "./Box";
import Button from "./Button";
import detectPosition from "./detectPosition";
import { usePositionContext } from "./PositionProvider";
import { tracker } from './tracker';

function App() {
  const { setPosition, position } = usePositionContext();

  if (!position || !setPosition) {
    return <>loading...</>;
  }

  let sourceCodePositionString = '';
  let relevantFrame = null;
  let maxDigits = 0;
  let spacing = 3;
  let fileName = "";
  if(position.mappedStackFrames && position.mappedStackFrames.length > 1) {
    relevantFrame = position.mappedStackFrames[1];
    fileName = relevantFrame.fileName.replace('home/surai/Projects/objectiv/objectiv-analytics/tracker/developer-tools/tests/cra-app-for-fixtures/', '')
    sourceCodePositionString += `Function: ${relevantFrame.functionName}\n`;
    sourceCodePositionString += `File: ${fileName}\n`
    sourceCodePositionString += `Line: ${relevantFrame.lineNumber}\n`
    sourceCodePositionString += `Column: ${relevantFrame.columnNumber}\n`
    if (relevantFrame.sourceCodePreview) {
      maxDigits = Math.max(...relevantFrame.sourceCodePreview.map(line => line.lineNumber)).toString().length;
    }
  }

  return (
    <tracker.div id={'app'}>
      <header>
        <div style={{display: 'flex', flexDirection: 'row'}}>
          <div style={{padding: 20, marginRight: '20%', backgroundColor: 'lightgreen'}}>
            {/*<p>*/}
            {/*  /!* eslint-disable-next-line no-eval *!/*/}
            {/*  <button onClick={() => eval('console.log(JSON.stringify(new Error().stack))')}>Trigger eval exception</button>*/}
            {/*</p>*/}
            <p>
              <Button>Button Component</Button>
            </p>
            <p>
              <tracker.button
                id={'inline-button'}
                onClick={
                  async () => {
                    const position = await detectPosition()
                    setPosition(position);
                  }
                }
              >Inline &lt;button&gt;</tracker.button>
            </p>
            <Box />
          </div>
          <div style={{flex: 1, color: "black"}}>
            <h1>Source Code Info:</h1>
            <pre><code>{sourceCodePositionString}</code></pre>
            {relevantFrame?.sourceCodePreview && <h2>{fileName ?? 'Code Preview'}</h2>}
            {relevantFrame?.sourceCodePreview?.map((sourceCodeLine, index) => {
              const formattedLine = String(sourceCodeLine.lineNumber).padStart(maxDigits, ` `) + String().padStart(spacing, ' ') + sourceCodeLine.line;

              if(sourceCodeLine.isFrameTarget) {
                return <pre key={index}><code style={{backgroundColor: 'PapayaWhip'}}>{formattedLine.padEnd(formattedLine.length + maxDigits + spacing)}</code></pre>
              }
              return <pre key={index}><code>{formattedLine}</code></pre>
            })}
          </div>
        </div>
      </header>
      <hr style={{marginTop: 200}}/>
      <aside>
        <h1>Mapped Stack Frames</h1>
        <pre >{JSON.stringify(position?.mappedStackFrames, null, 2)}</pre>
        <hr/>
        <h1>Raw Stack Frames</h1>
        <pre >{JSON.stringify(position?.rawStackFrames, null, 2)}</pre>
        <hr/>
        <h1>Stack Trace</h1>
        <pre >{position?.stackTrace}</pre>
      </aside>
    </tracker.div>
  );
}

export default App;
