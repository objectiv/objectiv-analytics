import React from 'react';
import { useElementContext } from './TrackerElementContextProvider';

const rootPath = 'home/surai/Projects/objectiv/objectiv-analytics/tracker/developer-tools/tests/cra-app-for-fixtures/';

export const ElementContext = (
  props: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>
) => {
  const { elementContext } = useElementContext();

  if (!elementContext.mappedStackFrames || elementContext.mappedStackFrames.length < 1) {
    return null;
  }

  const relevantFrame = elementContext.mappedStackFrames[1];
  const shortFileName = relevantFrame.fileName.replace(rootPath, '');

  let spacing = 3;
  let maxDigits = 0;
  if (relevantFrame.sourceCodePreview) {
    maxDigits = Math.max(...relevantFrame.sourceCodePreview.map((line) => line.lineNumber)).toString().length;
  }

  return (
    <div {...props} style={{ padding: 20 }}>
      <div style={{ display: 'flex', paddingBottom: 20 }}>
        <div style={{ paddingRight: 100 }}>
          <h2>Source Code Info</h2>
          <code>
            Function: <strong>{relevantFrame.functionName}</strong>
            <br />
            File: <strong>{shortFileName}</strong>
            <br />
            Line: <strong>{relevantFrame.lineNumber}</strong>
            <br />
            Column: <strong>{relevantFrame.columnNumber}</strong>
            <br />
          </code>
        </div>
        {elementContext.elementMetadata?.elementId && (
          <div>
            <h2>Element Info</h2>
            <code>
              Element Id: <strong>{elementContext.elementMetadata.elementId}</strong>
              <br />
              Element Type: <strong>&lt;{elementContext.elementMetadata.elementType}&gt;</strong>
              <br />
              Context Type: <strong>{elementContext.elementMetadata.contextType}</strong>
              <br />
              Context Id: <strong>{elementContext.elementMetadata.contextId}</strong>
              <br />
            </code>
          </div>
        )}
      </div>

      {relevantFrame.sourceCodePreview && (
        <>
          <h2>Source code preview</h2>
          <h3>{shortFileName}</h3>

          <div style={{backgroundColor: "aliceblue", padding: 20}}>
            {relevantFrame.sourceCodePreview.map((sourceCodeLine, index) => {
              const formattedLine =
                String(sourceCodeLine.lineNumber).padStart(maxDigits + 2, ` `) +
                '|' +
                String().padStart(spacing, ' ') +
                sourceCodeLine.line;

              if (sourceCodeLine.isFrameTarget) {
                return (
                  <pre key={index} style={{ margin: 5 }}>
              <code key={index} style={{ backgroundColor: 'PapayaWhip' }}>
                {'>' + formattedLine.padEnd(formattedLine.length + maxDigits + spacing).slice(1)}
              </code>
            </pre>
                );
              }
              return (
                <pre key={index} style={{ margin: 5 }}>
            <code>{formattedLine}</code>
          </pre>
              );
            })}
          </div>
        </>
      )}

      <hr style={{ marginTop: 200 }} />
      <aside>
        <h1>Mapped Stack Frames</h1>
        <pre>{JSON.stringify(elementContext?.mappedStackFrames, null, 2)}</pre>
        <hr />
        <h1>Raw Stack Frames</h1>
        <pre>{JSON.stringify(elementContext?.rawStackFrames, null, 2)}</pre>
        <hr />
        <h1>Stack Trace</h1>
        <pre>{elementContext?.stackTrace}</pre>
      </aside>
    </div>
  );
};
