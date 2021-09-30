import {
  makeApplicationLoadedEvent,
  makeClickEvent,
  makeInputChangeEvent,
  makeSectionContext,
  makeSectionHiddenEvent,
  makeSectionVisibleEvent,
  makeURLChangeEvent,
  makeVideoPauseEvent,
  makeVideoStartEvent,
} from '@objectiv/tracker-core';
import {
  BrowserTracker,
  getTracker,
  makeTracker,
  TaggingAttribute,
  trackApplicationLoaded,
  trackClick,
  trackEvent,
  trackInputChange,
  trackSectionHidden,
  trackSectionVisible,
  trackURLChange,
  trackVideoPause,
  trackVideoStart,
  trackVisibility,
} from '../src';

describe('trackEvent', () => {
  const testElement = document.createElement('div');
  document.body.appendChild(testElement);

  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: 'test', endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  it('should console.error if a Tracker instance cannot be retrieved and was not provided either', async () => {
    window.objectiv.trackers.delete('test');
    expect(getTracker()).toBeUndefined();
    jest.spyOn(console, 'error');

    const parameters = { eventFactory: makeClickEvent, element: testElement };
    trackEvent(parameters);

    expect(console.error).toHaveBeenCalledTimes(2);
    expect(console.error).toHaveBeenNthCalledWith(
      1,
      '｢objectiv:TrackerRepository｣ No Tracker Instances. Use `makeTracker` to create one.'
    );
    expect(console.error).toHaveBeenNthCalledWith(
      2,
      new TypeError("Cannot read property 'trackEvent' of undefined"),
      parameters
    );

    trackEvent({ ...parameters, onError: console.error });
    expect(console.error).toHaveBeenCalledTimes(4);
    expect(console.error).toHaveBeenNthCalledWith(
      4,
      new ReferenceError("Cannot read property 'trackEvent' of undefined")
    );
  });

  it('should use the global tracker instance if available', () => {
    expect(getTracker().trackEvent).not.toHaveBeenCalled();

    trackEvent({ eventFactory: makeClickEvent, element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, makeClickEvent());
  });

  it('should use the given tracker instance', () => {
    const trackerOverride = new BrowserTracker({ applicationId: 'override', endpoint: 'override' });
    jest.spyOn(trackerOverride, 'trackEvent');

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(trackerOverride.trackEvent).not.toHaveBeenCalled();

    trackEvent({ eventFactory: makeClickEvent, element: testElement, tracker: trackerOverride });

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(trackerOverride.trackEvent).toHaveBeenCalledTimes(1);
    expect(trackerOverride.trackEvent).toHaveBeenNthCalledWith(1, makeClickEvent());
  });

  it('should track Tracked Elements with a location stack', () => {
    const testDivToTrack = document.createElement('div');
    testDivToTrack.setAttribute(TaggingAttribute.context, JSON.stringify(makeSectionContext({ id: 'test' })));

    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, JSON.stringify(makeSectionContext({ id: 'div' })));

    const midSection = document.createElement('section');
    midSection.setAttribute(TaggingAttribute.context, JSON.stringify(makeSectionContext({ id: 'mid' })));

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');
    topSection.setAttribute(TaggingAttribute.context, JSON.stringify(makeSectionContext({ id: 'top' })));

    div.appendChild(testDivToTrack);
    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);
    document.body.appendChild(topSection);

    trackEvent({ eventFactory: makeClickEvent, element: testDivToTrack });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        ...makeClickEvent(),
        location_stack: expect.arrayContaining([
          { __location_context: true, __section_context: true, _type: 'SectionContext', id: 'top' },
          { __location_context: true, __section_context: true, _type: 'SectionContext', id: 'mid' },
          { __location_context: true, __section_context: true, _type: 'SectionContext', id: 'div' },
          { __location_context: true, __section_context: true, _type: 'SectionContext', id: 'test' },
        ]),
      })
    );
  });

  it('should track regular Elements with a location stack if their parents are Tracked Elements', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, JSON.stringify(makeSectionContext({ id: 'div' })));

    const midSection = document.createElement('section');
    midSection.setAttribute(TaggingAttribute.context, JSON.stringify(makeSectionContext({ id: 'mid' })));

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');
    topSection.setAttribute(TaggingAttribute.context, JSON.stringify(makeSectionContext({ id: 'top' })));

    div.appendChild(testElement);
    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);
    document.body.appendChild(topSection);

    trackEvent({ eventFactory: makeClickEvent, element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        ...makeClickEvent(),
        location_stack: expect.arrayContaining([
          { __location_context: true, __section_context: true, _type: 'SectionContext', id: 'top' },
          { __location_context: true, __section_context: true, _type: 'SectionContext', id: 'mid' },
          { __location_context: true, __section_context: true, _type: 'SectionContext', id: 'div' },
        ]),
      })
    );
  });

  it('should track without a location stack', () => {
    const div = document.createElement('div');

    div.appendChild(testElement);
    document.body.appendChild(div);

    trackEvent({ eventFactory: makeClickEvent, element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeClickEvent()));
  });

  it('should track a Click Event', () => {
    trackClick({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeClickEvent()));
  });

  it('should track a Input Change Event', () => {
    trackInputChange({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeInputChangeEvent()));
  });

  it('should track a Section Visible Event', () => {
    trackSectionVisible({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeSectionVisibleEvent()));
  });

  it('should track a Section Hidden Event', () => {
    trackSectionHidden({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeSectionHiddenEvent()));
  });

  it('should track a Video Start Event', () => {
    trackVideoStart({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeVideoStartEvent()));
  });

  it('should track a Video Pause Event', () => {
    trackVideoPause({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeVideoPauseEvent()));
  });

  it('should track either a Section Visible or Section Hidden Event based on the given state', () => {
    trackVisibility({ element: testElement, isVisible: true });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeSectionVisibleEvent()));

    trackVisibility({ element: testElement, isVisible: false });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(2);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(2, expect.objectContaining(makeSectionHiddenEvent()));
  });

  it('should track an Application Loaded Event', () => {
    trackApplicationLoaded();

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeApplicationLoadedEvent()));

    trackApplicationLoaded({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(2);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(2, expect.objectContaining(makeApplicationLoadedEvent()));
  });

  it('should track a URL Change Event', () => {
    trackURLChange();

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeURLChangeEvent()));

    trackURLChange({ element: testElement });

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(2);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(2, expect.objectContaining(makeURLChangeEvent()));
  });
});
