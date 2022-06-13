/*
 * Copyright 2021-2022 Objectiv B.V.
 * @jest-environment node
 */
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { makePathContext, Tracker, TrackerEvent } from '@objectiv/tracker-core';
import { PathContextFromURLPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('PathContextFromURLPlugin - node', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should instantiate as unusable', () => {
    const testPathContextFromURLPlugin = new PathContextFromURLPlugin();
    expect(testPathContextFromURLPlugin.isUsable()).toBe(false);
  });

  it('when unusable, should not initialize and log an error message', () => {
    const testPathContextFromURLPlugin = new PathContextFromURLPlugin();
    testPathContextFromURLPlugin.initialize(
      new Tracker({
        applicationId: 'app-id',
        plugins: [],
        trackApplicationContext: false,
      })
    );
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:PathContextFromURLPlugin｣ Cannot initialize. Plugin is not usable (document: undefined).'
    );
  });

  it('when unusable, should not validate and log an error message', () => {
    const testPathContextFromURLPlugin = new PathContextFromURLPlugin();
    const testEvent = new TrackerEvent({ _type: 'test-event' });
    testPathContextFromURLPlugin.validate(testEvent);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:PathContextFromURLPlugin｣ Cannot validate. Plugin is not usable (document: undefined).'
    );
  });

  it('when unusable, should not enrich and log an error message', () => {
    const testPathContextFromURLPlugin = new PathContextFromURLPlugin();
    testPathContextFromURLPlugin.enrich(new TrackerEvent({ _type: 'test-event' }));
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:PathContextFromURLPlugin｣ Cannot enrich. Plugin is not usable (document: undefined).'
    );
  });

  describe('Validation', () => {
    it('should not fail when given TrackerEvent does not have PathContext but plugin is not usable', () => {
      const testPathContextPlugin = new PathContextFromURLPlugin();
      const eventWithoutPathContext = new TrackerEvent({ _type: 'test' });

      jest.resetAllMocks();

      testPathContextPlugin.validate(eventWithoutPathContext);

      expect(MockConsoleImplementation.groupCollapsed).not.toHaveBeenCalled();
    });

    it('should not fail when given TrackerEvent has multiple PathContexts', () => {
      const testPathContextPlugin = new PathContextFromURLPlugin();
      const eventWithDuplicatedPathContext = new TrackerEvent({
        _type: 'test',
        global_contexts: [makePathContext({ id: '/test' }), makePathContext({ id: '/test' })],
      });

      jest.resetAllMocks();

      testPathContextPlugin.validate(eventWithDuplicatedPathContext);

      expect(MockConsoleImplementation.groupCollapsed).not.toHaveBeenCalled();
    });
  });

  describe('Without developer tools', () => {
    let objectivGlobal = globalThis.objectiv;

    beforeEach(() => {
      jest.clearAllMocks();
      globalThis.objectiv = undefined;
    });

    afterEach(() => {
      globalThis.objectiv = objectivGlobal;
    });

    it('when unusable, should not initialize and not log', () => {
      const testPathContextPlugin = new PathContextFromURLPlugin();
      testPathContextPlugin.initialize(
        new Tracker({
          applicationId: 'app-id',
          plugins: [],
          trackApplicationContext: false,
        })
      );
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('when unusable, should not validate and not log', () => {
      const testPathContextPlugin = new PathContextFromURLPlugin();
      const testEvent = new TrackerEvent({ _type: 'test-event' });
      testPathContextPlugin.validate(testEvent);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('when unusable, should not enrich and not log', () => {
      const testPathContextFromURLPlugin = new PathContextFromURLPlugin();
      testPathContextFromURLPlugin.enrich(new TrackerEvent({ _type: 'test-event' }));
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
