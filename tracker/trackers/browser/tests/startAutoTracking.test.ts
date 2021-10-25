import { makeSectionContext, makeSectionVisibleEvent, makeURLChangeEvent } from '@objectiv/tracker-core';
import {
  BrowserTracker,
  makeTracker,
  makeMutationCallback,
  startAutoTracking,
  TaggingAttribute,
  getTracker, getTrackerRepository, stopAutoTracking, AutoTrackingState,
} from '../src';
import { makeTaggedElement } from './mocks/makeTaggedElement';

describe('startAutoTracking', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: 'test', endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  it('options', () => {
    startAutoTracking({ trackApplicationLoaded: false, trackURLChanges: false });
    stopAutoTracking();
    startAutoTracking({ trackURLChanges: false });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoaded: false });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoaded: true, trackURLChanges: true });
    stopAutoTracking();
    startAutoTracking({ trackURLChanges: true });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoaded: true });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoaded: true, trackURLChanges: false });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoaded: false, trackURLChanges: true });
    stopAutoTracking();
    startAutoTracking({});
    stopAutoTracking();
    startAutoTracking();
    stopAutoTracking();
    stopAutoTracking();
  });

  it('should console.error', () => {
    jest.spyOn(console, 'error');
    startAutoTracking();
    expect(console.error).not.toHaveBeenCalled()
    // @ts-ignore
    AutoTrackingState.observerInstance = {
      disconnect: () => { throw new Error('oops') }
    }
    stopAutoTracking();
    expect(console.error).toHaveBeenCalledTimes(1)
  });

  it('should not track application loaded event', () => {
    const tracker = new BrowserTracker({ endpoint: 'endpoint', applicationId: 'app' });
    jest.spyOn(tracker, 'trackEvent');

    startAutoTracking({ trackApplicationLoaded: false, trackURLChanges: false });

    expect(tracker.trackEvent).not.toHaveBeenCalled();
  });
});

describe('makeMutationCallback - url changes', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: 'test', endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  it('should not track url changes', () => {
    const mutationCallback = makeMutationCallback(false);
    const mutationObserver = new MutationObserver(mutationCallback);

    Object.defineProperty(window, 'location', {
      value: {
        href: 'http://localhost/new',
      },
    });
    mutationCallback([], mutationObserver);

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should track url changes with the global tracker', () => {
    const mutationCallback = makeMutationCallback(true);
    const mutationObserver = new MutationObserver(mutationCallback);

    Object.defineProperty(window, 'location', {
      value: {
        href: 'http://localhost/new',
      },
    });
    mutationCallback([], mutationObserver);

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, makeURLChangeEvent());
  });
});

describe('makeMutationCallback - new nodes', () => {
  it('should track newly added nodes that are Elements and visibility for existing nodes', () => {
    const tracker = new BrowserTracker({ endpoint: 'endpoint', applicationId: 'app' });
    const trackerRepository = getTrackerRepository();
    trackerRepository.add(tracker);
    trackerRepository.setDefault(tracker.trackerId);
    jest.spyOn(tracker, 'trackEvent');
    const mutationCallback = makeMutationCallback(false);
    const mutationObserver = new MutationObserver(mutationCallback);

    const sectionContext = makeSectionContext({ id: 'div' });
    const trackedDiv = makeTaggedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');

    const mockedMutationRecord: MutationRecord = {
      // @ts-ignore
      addedNodes: [document.createComment('comment'), trackedDiv],
      // @ts-ignore
      removedNodes: [document.createComment('comment')],
      attributeName: TaggingAttribute.trackVisibility,
      target: trackedDiv,
    };
    mutationCallback([mockedMutationRecord], mutationObserver);

    expect(tracker.trackEvent).toHaveBeenCalledTimes(2);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(
      1,
      makeSectionVisibleEvent({
        location_stack: [
          expect.objectContaining({
            _type: sectionContext._type,
            id: sectionContext.id,
          }),
        ],
      })
    );
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(
      2,
      makeSectionVisibleEvent({
        location_stack: [
          expect.objectContaining({
            _type: sectionContext._type,
            id: sectionContext.id,
          }),
        ],
      })
    );
  });

  it('should console.error if there are no Trackers', () => {
    jest.spyOn(console, 'error');
    getTrackerRepository().trackersMap = new Map();
    const mutationCallback = makeMutationCallback(false);
    const mutationObserver = new MutationObserver(mutationCallback);

    const trackedDiv = makeTaggedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');

    const mockedMutationRecord: MutationRecord = {
      // @ts-ignore
      addedNodes: [trackedDiv],
      // @ts-ignore
      removedNodes: [],
      attributeName: TaggingAttribute.trackVisibility,
      target: trackedDiv,
    };
    jest.clearAllMocks();
    expect(console.error).not.toHaveBeenCalled();
    mutationCallback([mockedMutationRecord], mutationObserver);
    expect(console.error).toHaveBeenCalledTimes(2);
    expect(console.error).toHaveBeenNthCalledWith(1, `｢objectiv:TrackerRepository｣ There are no Trackers.`);
    expect(console.error).toHaveBeenNthCalledWith(2, new Error(`No Tracker found. Please create one via \`makeTracker\`.`), undefined);
  });
});
