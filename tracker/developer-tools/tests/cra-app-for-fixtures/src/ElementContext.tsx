import React from 'react';
import superjson from "superjson";
import { ContextInstance, TrackingAttribute, traverseAndCollectParentsTrackingAttributes } from './tracker';
import { useElementContext } from './TrackerElementContextProvider';

const rootPath = 'home/surai/Projects/objectiv/objectiv-analytics/tracker/developer-tools/tests/cra-app-for-fixtures/';

export const ElementContext = (
  props: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>
) => {
  const { elementContext } = useElementContext();

  const element = document.querySelector(
    `[${TrackingAttribute.objectivElementId}='${elementContext.elementMetadata?.objectivElementId}']`
  );
  const parentElementsMetadata = traverseAndCollectParentsTrackingAttributes(element);

  document.querySelectorAll(`[${TrackingAttribute.objectivElementId}]`).forEach((trackedElement) => {
    if (trackedElement instanceof HTMLElement) {
      trackedElement.style.boxShadow = '';
      trackedElement.style.opacity = elementContext.elementMetadata ? '.7' : '1';
    }
  });

  parentElementsMetadata.forEach((parentMetadata) => {
    const parentElement = document.querySelector(
      `[${TrackingAttribute.objectivElementId}='${parentMetadata.objectivElementId}']`
    );
    if (parentElement instanceof HTMLElement) {
      parentElement.style.opacity = '1';
      parentElement.style.boxShadow = '0 0 0 3px red';
    }
  });

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
    <div {...props} style={{ padding: 20, zoom: 1.2 }}>
      <div style={{ display: 'flex', paddingBottom: 5 }}>
        <div style={{ flex: 0.55 }}>
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
        {elementContext.elementMetadata?.objectivElementId && (
          <>
            <div style={{ flex: 0.8 }}>
              <h2>Tracking Metadata</h2>
              <code>
                Element Id: <strong>{elementContext.elementMetadata.objectivElementId}</strong>
                <br />
                Context Type: <strong>{superjson.parse<ContextInstance>(elementContext.elementMetadata.objectivContext ?? '').__context_type}</strong>
                <br />
                Context Id: <strong>{superjson.parse<ContextInstance>(elementContext.elementMetadata.objectivContext ?? '').id}</strong>
                <br />
                Component Name: <strong>{elementContext.elementMetadata.objectivComponent}</strong>
              </code>
            </div>

            <div style={{ flex: 1 }}>
              <h2>Component Stack</h2>
              <code>
                <ul style={{ marginLeft: -24 }}>
                  {parentElementsMetadata?.reverse().map((parentElementMetadata, index) => (
                    <li key={index} style={{ marginLeft: 12, marginTop: 5 }}>
                      {parentElementMetadata.objectivComponent} -{' '}
                      <strong>{superjson.parse<ContextInstance>(parentElementMetadata.objectivContext ?? '').__context_type}</strong> with id{' '}
                      <strong>{superjson.parse<ContextInstance>(parentElementMetadata.objectivContext ?? '').id}</strong>
                    </li>
                  ))}
                </ul>
              </code>
            </div>
          </>
        )}
      </div>

      {relevantFrame.sourceCodePreview && (
        <>
          <h2>{shortFileName}</h2>

          <div style={{ backgroundColor: 'aliceblue', padding: 20 }}>
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
