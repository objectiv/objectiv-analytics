/*
 * Copyright 2021-2022 Objectiv B.V.
 * @jest-environment node
 */
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID, TrackerEvent } from '@objectiv/tracker-core';
import { PathContextFromURLPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('PathContextFromURLPlugin - node', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should instantiate as unusable', () => {
    const testPathContextFromURLPlugin = new PathContextFromURLPlugin();
    expect(testPathContextFromURLPlugin.isUsable()).toBe(false);
  });

  it('when unusable, should not enrich and log an error message', () => {
    const testPathContextFromURLPlugin = new PathContextFromURLPlugin();
    testPathContextFromURLPlugin.enrich(
      new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() })
    );
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:PathContextFromURLPlugin｣ Cannot enrich. Plugin is not usable (document: undefined).'
    );
  });

  describe('Without developer tools', () => {
    let objectivGlobal = globalThis.objectiv;

    beforeEach(() => {
      jest.clearAllMocks();
      globalThis.objectiv.devTools = undefined;
    });

    afterEach(() => {
      globalThis.objectiv = objectivGlobal;
    });

    it('should not log', () => {
      const testPathContextPlugin = new PathContextFromURLPlugin();
      testPathContextPlugin.initialize();
      expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
    });

    it('when unusable, should not enrich and not log', () => {
      const testPathContextFromURLPlugin = new PathContextFromURLPlugin();
      testPathContextFromURLPlugin.enrich(
        new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() })
      );
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
