import { createElement, FC, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';

// TODO get this from Schema._context_type literals
enum ContextType {
  section = 'SectionContext',
  button = 'ButtonContext',
  link = 'LinkContext',
}

export type TrackerElementMetadata = {
  elementId: string;
  elementType: JSXElement;
  contextType: ContextType;
  contextId: string;
};

export type TrackerElementTarget = EventTarget & {
  objectiv: string;
};

export const TrackerStore = new Map<string, TrackerElementMetadata>();

type JSXElement = keyof JSX.IntrinsicElements;
type ReactHTMLProps = React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
type RequireId = { id: string; objectivContextId?: string };
type RequireObjectivContextId = { id: string; objectivContextId: string };
type TrackerElementProps = ReactHTMLProps & (RequireObjectivContextId | RequireId);

const TrackerElementFactory: (elementType: JSXElement, contextType: ContextType) => FC<TrackerElementProps> = (
  elementType: JSXElement,
  contextType: ContextType
) =>
  function TrackerElement(props: TrackerElementProps) {
    const { id, objectivContextId, ...otherProps } = props;
    const contextId = id ?? objectivContextId;

    if (!contextId) {
      throw new Error(`Tracker Element (${elementType}) requires either 'id' or 'objectivContextId' to be set.`);
    }

    const elementId = useRef(uuidv4()).current;
    if (!TrackerStore.has(elementId)) {
      TrackerStore.set(elementId, { elementId, elementType, contextType, contextId });
      console.log(`Tracking Element ${elementId}: ${elementType}#${contextId}`);
    }

    return createElement(elementType, {
      ...otherProps,
      'data-objectiv': elementId,
    });
  };

export const TrackerButton = TrackerElementFactory('button', ContextType.button);
export const TrackerDiv = TrackerElementFactory('div', ContextType.section);
export const TrackerHeader = TrackerElementFactory('header', ContextType.section);
export const TrackerLink = TrackerElementFactory('link', ContextType.link);
export const TrackerSpan = TrackerElementFactory('span', ContextType.section);

export const tracker = {
  button: TrackerButton,
  div: TrackerDiv,
  header: TrackerHeader,
  link: TrackerLink,
  span: TrackerSpan,
};
