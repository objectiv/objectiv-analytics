/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import {
  EventName,
  generateGUID,
  LocationContextName,
  makeApplicationLoadedEvent,
  makeContentContext,
  makeFailureEvent,
  makeHiddenEvent,
  makeInputChangeEvent,
  makeInteractiveEvent,
  makeMediaEvent,
  makeMediaLoadEvent,
  makeMediaPauseEvent,
  makeMediaStartEvent,
  makeMediaStopEvent,
  makeNonInteractiveEvent,
  makePressEvent,
  makeSuccessEvent,
  makeVisibleEvent,
} from '@objectiv/tracker-core';
import {
  BrowserTracker,
  getTracker,
  getTrackerRepository,
  makeTracker,
  TaggingAttribute,
  trackApplicationLoadedEvent,
  trackEvent,
  trackFailureEvent,
  trackHiddenEvent,
  trackInputChangeEvent,
  trackInteractiveEvent,
  trackMediaEvent,
  trackMediaLoadEvent,
  trackMediaPauseEvent,
  trackMediaStartEvent,
  trackMediaStopEvent,
  trackNonInteractiveEvent,
  trackPressEvent,
  trackSuccessEvent,
  trackVisibility,
  trackVisibleEvent,
} from '../src';
import { makeTaggedElement } from './mocks/makeTaggedElement';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('trackEvent', () => {
  const testElement = document.createElement('div');

  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: generateGUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  afterEach(() => {
    getTrackerRepository().trackersMap = new Map();
    getTrackerRepository().defaultTracker = undefined;
    jest.resetAllMocks();
  });

  it('should track from a bag of attributes', () => {
    expect(getTracker().trackEvent).not.toHaveBeenCalled();

    trackEvent({ event: { _type: EventName.PressEvent }, element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, {
      _type: 'PressEvent',
    });
  });

  it('should use the global tracker instance if available', () => {
    expect(getTracker().trackEvent).not.toHaveBeenCalled();

    trackEvent({ event: makePressEvent(), element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        global_contexts: [],
        location_stack: [],
      })
    );
  });

  it('should use the given location stack instead of the element DOM', () => {
    expect(getTracker().trackEvent).not.toHaveBeenCalled();

    const mainSection = makeTaggedElement('main', 'main', 'section');
    const div = document.createElement('div');
    const parentSection = makeTaggedElement('parent', 'parent', 'div');
    const section = document.createElement('section');
    const childSection = makeTaggedElement('child', 'child', 'span');
    const button = makeTaggedElement('button', 'button', 'button', true);

    mainSection.appendChild(div);
    div.appendChild(parentSection);
    parentSection.appendChild(section);
    section.appendChild(childSection);
    childSection.appendChild(button);

    trackEvent({ event: makePressEvent(), element: button });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        global_contexts: [],
        location_stack: [
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'main' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'parent' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'child' }),
          expect.objectContaining({ _type: LocationContextName.PressableContext, id: 'button' }),
        ],
      })
    );

    trackEvent({ event: makePressEvent({ location_stack: [makeContentContext({ id: 'custom' })] }), element: button });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(2);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        global_contexts: [],
        location_stack: [expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'custom' })],
      })
    );

    trackEvent({ event: makePressEvent({ location_stack: [makeContentContext({ id: 'custom' })] }) });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(3);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      3,
      expect.objectContaining({
        _type: 'PressEvent',
        global_contexts: [],
        location_stack: [expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'custom' })],
      })
    );
  });

  it('should use the given tracker instance', () => {
    const trackerOverride = new BrowserTracker({ applicationId: 'override', transport: new LogTransport() });
    jest.spyOn(trackerOverride, 'trackEvent');

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(trackerOverride.trackEvent).not.toHaveBeenCalled();

    trackEvent({ event: makePressEvent(), element: testElement, tracker: trackerOverride });

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(trackerOverride.trackEvent).toHaveBeenCalledTimes(1);
    expect(trackerOverride.trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        global_contexts: [],
        location_stack: [],
      })
    );
  });

  it('should track Tagged Elements with a location stack', () => {
    const testDivToTrack = document.createElement('div');
    testDivToTrack.setAttribute(TaggingAttribute.context, JSON.stringify(makeContentContext({ id: 'test' })));

    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, JSON.stringify(makeContentContext({ id: 'div' })));

    const midSection = document.createElement('section');
    midSection.setAttribute(TaggingAttribute.context, JSON.stringify(makeContentContext({ id: 'mid' })));

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');
    topSection.setAttribute(TaggingAttribute.context, JSON.stringify(makeContentContext({ id: 'top' })));

    div.appendChild(testDivToTrack);
    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);

    trackEvent({ event: makePressEvent(), element: testDivToTrack });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        ...makePressEvent(),
        location_stack: expect.arrayContaining([
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'top' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'mid' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'div' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'test' }),
        ]),
      })
    );
  });

  it('should track regular Elements with a location stack if their parents are Tagged Elements', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, JSON.stringify(makeContentContext({ id: 'div' })));

    const midSection = document.createElement('section');
    midSection.setAttribute(TaggingAttribute.context, JSON.stringify(makeContentContext({ id: 'mid' })));

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');
    topSection.setAttribute(TaggingAttribute.context, JSON.stringify(makeContentContext({ id: 'top' })));

    div.appendChild(testElement);
    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);

    trackEvent({ event: makePressEvent(), element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        ...makePressEvent(),
        location_stack: expect.arrayContaining([
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'top' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'mid' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'div' }),
        ]),
      })
    );
  });

  it('should track without a location stack', () => {
    const div = document.createElement('div');

    div.appendChild(testElement);

    trackEvent({ event: makePressEvent(), element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makePressEvent()));
  });

  it('should track a ClickEvent', () => {
    trackPressEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makePressEvent()));
  });

  it('should track a InputChangeEvent', () => {
    trackInputChangeEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeInputChangeEvent()));
  });

  it('should track an InteractiveEvent', () => {
    trackInteractiveEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeInteractiveEvent()));
  });

  it('should track a VisibleEvent', () => {
    trackVisibleEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeVisibleEvent()));
  });

  it('should track a HiddenEvent', () => {
    trackHiddenEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeHiddenEvent()));
  });

  it('should track a MediaEvent', () => {
    trackMediaEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeMediaEvent()));
  });

  it('should track a MediaLoadEvent', () => {
    trackMediaLoadEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeMediaLoadEvent()));
  });

  it('should track a MediaStartEvent', () => {
    trackMediaStartEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeMediaStartEvent()));
  });

  it('should track a MediaPauseEvent', () => {
    trackMediaPauseEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeMediaPauseEvent()));
  });

  it('should track a MediaStopEvent', () => {
    trackMediaStopEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeMediaStopEvent()));
    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
  });

  it('should track an NonInteractiveEvent', () => {
    trackNonInteractiveEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeNonInteractiveEvent()));
  });

  it('should track either a VisibleEvent or HiddenEvent based on the given state', () => {
    trackVisibility({ element: testElement, isVisible: true });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeVisibleEvent()));

    trackVisibility({ element: testElement, isVisible: false });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(2);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(2, expect.objectContaining(makeHiddenEvent()));
  });

  it('should track an ApplicationLoadedEvent', () => {
    trackApplicationLoadedEvent();

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeApplicationLoadedEvent()));

    trackApplicationLoadedEvent({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(2);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(2, expect.objectContaining(makeApplicationLoadedEvent()));
  });

  it('should track a SuccessCompletedEvent', () => {
    trackSuccessEvent({ message: 'ok' });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(makeSuccessEvent({ message: 'ok' }))
    );

    trackSuccessEvent({ message: 'ok', element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(2);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining(makeSuccessEvent({ message: 'ok' }))
    );
  });

  it('should track an FailureEvent', () => {
    trackFailureEvent({ message: 'ko' });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(makeFailureEvent({ message: 'ko' }))
    );

    trackFailureEvent({ message: 'ko', element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(2);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining(makeFailureEvent({ message: 'ko' }))
    );
  });
});

describe('trackEvent', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  const testElement = document.createElement('div');

  getTrackerRepository().trackersMap = new Map();
  getTrackerRepository().defaultTracker = undefined;

  it('should TrackerConsole.error if a Tracker instance cannot be retrieved and was not provided either', () => {
    const parameters = { event: makePressEvent(), element: testElement };
    trackEvent(parameters);

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      1,
      '｢objectiv:TrackerRepository｣ There are no Trackers.'
    );
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      2,
      new Error('No Tracker found. Please create one via `makeTracker`.'),
      parameters
    );

    trackEvent({ ...parameters, onError: MockConsoleImplementation.error });
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(4);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      4,
      new Error('No Tracker found. Please create one via `makeTracker`.')
    );
  });
});
