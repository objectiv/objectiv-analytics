import {
  makeApplicationLoadedEvent,
  makeClickEvent,
  makeDeviceContext,
  makeDocumentLoadedEvent,
  makeInputChangeEvent,
  makeSectionContext,
  makeSectionHiddenEvent,
  makeSectionVisibleEvent,
  makeURLChangedEvent,
  makeVideoEvent,
  makeVideoLoadEvent,
  makeVideoPauseEvent,
  makeVideoStartEvent,
  makeVideoStopEvent,
} from '../src';

const sectionA = makeSectionContext({ id: 'A' });
const device = makeDeviceContext({ userAgent: '123' });

describe('Event Factories', () => {
  it('DocumentLoadedEvent', () => {
    expect(makeDocumentLoadedEvent()).toStrictEqual({
      _interactive_event: false,
      event: 'DocumentLoadedEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeDocumentLoadedEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: false,
      event: 'DocumentLoadedEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('URLChangedEvent', () => {
    expect(makeURLChangedEvent()).toStrictEqual({
      _interactive_event: false,
      event: 'URLChangedEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeURLChangedEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: false,
      event: 'URLChangedEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('ApplicationLoadedEvent', () => {
    expect(makeApplicationLoadedEvent()).toStrictEqual({
      _interactive_event: false,
      event: 'ApplicationLoadedEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeApplicationLoadedEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: false,
      event: 'ApplicationLoadedEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('SectionVisibleEvent', () => {
    expect(makeSectionVisibleEvent()).toStrictEqual({
      _interactive_event: false,
      event: 'SectionVisibleEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeSectionVisibleEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: false,
      event: 'SectionVisibleEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('SectionHiddenEvent', () => {
    expect(makeSectionHiddenEvent()).toStrictEqual({
      _interactive_event: false,
      event: 'SectionHiddenEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeSectionHiddenEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: false,
      event: 'SectionHiddenEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('VideoEvent', () => {
    expect(makeVideoEvent()).toStrictEqual({
      _interactive_event: false,
      _video_event: true,
      event: 'VideoEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeVideoEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: false,
      _video_event: true,
      event: 'VideoEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('VideoLoadEvent', () => {
    expect(makeVideoLoadEvent()).toStrictEqual({
      _interactive_event: false,
      _video_event: true,
      event: 'VideoLoadEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeVideoLoadEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: false,
      _video_event: true,
      event: 'VideoLoadEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('VideoStartEvent', () => {
    expect(makeVideoStartEvent()).toStrictEqual({
      _interactive_event: false,
      _video_event: true,
      event: 'VideoStartEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeVideoStartEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: false,
      _video_event: true,
      event: 'VideoStartEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('VideoStopEvent', () => {
    expect(makeVideoStopEvent()).toStrictEqual({
      _interactive_event: false,
      _video_event: true,
      event: 'VideoStopEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeVideoStopEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: false,
      _video_event: true,
      event: 'VideoStopEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('VideoPauseEvent', () => {
    expect(makeVideoPauseEvent()).toStrictEqual({
      _interactive_event: false,
      _video_event: true,
      event: 'VideoPauseEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeVideoPauseEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: false,
      _video_event: true,
      event: 'VideoPauseEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('ClickEvent', () => {
    expect(makeClickEvent()).toStrictEqual({
      _interactive_event: true,
      event: 'ClickEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeClickEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: true,
      event: 'ClickEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });

  it('InputChangeEvent', () => {
    expect(makeInputChangeEvent()).toStrictEqual({
      _interactive_event: true,
      event: 'InputChangeEvent',
      globalContexts: [],
      locationStack: [],
    });

    expect(makeInputChangeEvent({ locationStack: [sectionA], globalContexts: [device] })).toStrictEqual({
      _interactive_event: true,
      event: 'InputChangeEvent',
      globalContexts: [device],
      locationStack: [sectionA],
    });
  });
});
