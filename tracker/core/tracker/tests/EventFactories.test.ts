import {
  makeApplicationLoadedEvent,
  makeClickEvent,
  makeDeviceContext,
  makeDocumentLoadedEvent,
  makeInputChangeEvent,
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
  it('DocumentLoadedEvent', () => {
    expect(makeDocumentLoadedEvent()).toStrictEqual({
      __non_interactive_event: true,
      event: 'DocumentLoadedEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeDocumentLoadedEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      event: 'DocumentLoadedEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('URLChangedEvent', () => {
    expect(makeURLChangeEvent()).toStrictEqual({
      __non_interactive_event: true,
      event: 'URLChangeEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeURLChangeEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      event: 'URLChangeEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('ApplicationLoadedEvent', () => {
    expect(makeApplicationLoadedEvent()).toStrictEqual({
      __non_interactive_event: true,
      event: 'ApplicationLoadedEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeApplicationLoadedEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      event: 'ApplicationLoadedEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('SectionVisibleEvent', () => {
    expect(makeSectionVisibleEvent()).toStrictEqual({
      __non_interactive_event: true,
      event: 'SectionVisibleEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeSectionVisibleEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      event: 'SectionVisibleEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('SectionHiddenEvent', () => {
    expect(makeSectionHiddenEvent()).toStrictEqual({
      __non_interactive_event: true,
      event: 'SectionHiddenEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeSectionHiddenEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      event: 'SectionHiddenEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('VideoEvent', () => {
    expect(makeVideoEvent()).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      event: 'VideoEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVideoEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      event: 'VideoEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('VideoLoadEvent', () => {
    expect(makeVideoLoadEvent()).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      event: 'VideoLoadEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVideoLoadEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      event: 'VideoLoadEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('VideoStartEvent', () => {
    expect(makeVideoStartEvent()).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      event: 'VideoStartEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVideoStartEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      event: 'VideoStartEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('VideoStopEvent', () => {
    expect(makeVideoStopEvent()).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      event: 'VideoStopEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVideoStopEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      event: 'VideoStopEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('VideoPauseEvent', () => {
    expect(makeVideoPauseEvent()).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      event: 'VideoPauseEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVideoPauseEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __non_interactive_event: true,
      __video_event: true,
      event: 'VideoPauseEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('ClickEvent', () => {
    expect(makeClickEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __interactive_event: true,
      event: 'ClickEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });

  it('InputChangeEvent', () => {
    expect(makeInputChangeEvent({ location_stack: [sectionA], global_contexts: [device] })).toStrictEqual({
      __interactive_event: true,
      event: 'InputChangeEvent',
      global_contexts: [device],
      location_stack: [sectionA],
    });
  });
});
