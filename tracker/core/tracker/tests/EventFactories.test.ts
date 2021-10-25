import {
  makeAbortedEvent,
  makeApplicationLoadedEvent,
  makeClickEvent,
  makeCompletedEvent,
  makeDeviceContext,
  makeDocumentLoadedEvent,
  makeInputChangeEvent,
  makeInteractiveEvent,
  makeNonInteractiveEvent,
  makeSectionContext,
  makeSectionHiddenEvent,
  makeSectionVisibleEvent,
  makeURLChangeEvent,
  makeVideoEvent,
  makeVideoLoadEvent,
  makeVideoPauseEvent,
  makeVideoStartEvent,
  makeVideoStopEvent,
} from '../src';

const sectionA = makeSectionContext({ id: 'A' });
const device = makeDeviceContext({ id: 'device-123', user_agent: '123' });

describe('Event Factories', () => {
  it('InteractiveEvent', () => {
    expect(makeInteractiveEvent()).toStrictEqual({
      __interactive_event: true,
      _type: 'InteractiveEvent',
      global_contexts: [],
      location_stack: [],
    });
    expect(makeInteractiveEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __interactive_event: true,
      _type: 'InteractiveEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('NonInteractiveEvent', () => {
    expect(makeNonInteractiveEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'NonInteractiveEvent',
      global_contexts: [],
      location_stack: [],
    });
    expect(makeNonInteractiveEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'NonInteractiveEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('DocumentLoadedEvent', () => {
    expect(makeDocumentLoadedEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'DocumentLoadedEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeDocumentLoadedEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'DocumentLoadedEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('URLChangedEvent', () => {
    expect(makeURLChangeEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'URLChangeEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeURLChangeEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'URLChangeEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('ApplicationLoadedEvent', () => {
    expect(makeApplicationLoadedEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'ApplicationLoadedEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeApplicationLoadedEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'ApplicationLoadedEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('SectionVisibleEvent', () => {
    expect(makeSectionVisibleEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'SectionVisibleEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeSectionVisibleEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'SectionVisibleEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('SectionHiddenEvent', () => {
    expect(makeSectionHiddenEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'SectionHiddenEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeSectionHiddenEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'SectionHiddenEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('VideoEvent', () => {
    expect(makeVideoEvent()).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      _type: 'VideoEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVideoEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      _type: 'VideoEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('VideoLoadEvent', () => {
    expect(makeVideoLoadEvent()).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      _type: 'VideoLoadEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVideoLoadEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      _type: 'VideoLoadEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('VideoStartEvent', () => {
    expect(makeVideoStartEvent()).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      _type: 'VideoStartEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVideoStartEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      _type: 'VideoStartEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('VideoStopEvent', () => {
    expect(makeVideoStopEvent()).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      _type: 'VideoStopEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVideoStopEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      _type: 'VideoStopEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('VideoPauseEvent', () => {
    expect(makeVideoPauseEvent()).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      _type: 'VideoPauseEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVideoPauseEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      _type: 'VideoPauseEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('ClickEvent', () => {
    expect(makeClickEvent()).toStrictEqual({
      __interactive_event: true,
      _type: 'ClickEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeClickEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __interactive_event: true,
      _type: 'ClickEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('InputChangeEvent', () => {
    expect(makeInputChangeEvent()).toStrictEqual({
      __interactive_event: true,
      _type: 'InputChangeEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeInputChangeEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __interactive_event: true,
      _type: 'InputChangeEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('CompletedEvent', () => {
    expect(makeCompletedEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'CompletedEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeCompletedEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'CompletedEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('AbortedEvent', () => {
    expect(makeAbortedEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'AbortedEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeAbortedEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'AbortedEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });
});
