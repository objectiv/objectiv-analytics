/*
 * Copyright 2021-2022 Objectiv B.V.
 * @jest-environment node
 */
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID, TrackerEvent } from '@objectiv/tracker-core';
import { RootLocationContextFromURLPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('RootLocationContextFromURLPlugin - node', () => {
  beforeEach(() => {
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
  });

  it('should instantiate as unusable', () => {
    const testRootLocationContextFromURLPlugin = new RootLocationContextFromURLPlugin();
    expect(testRootLocationContextFromURLPlugin.isUsable()).toBe(false);
  });

  it('when unusable, should not enrich and log an error message', () => {
    const testRootLocationContextFromURLPlugin = new RootLocationContextFromURLPlugin();
    testRootLocationContextFromURLPlugin.enrich(
      new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() })
    );
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:RootLocationContextFromURLPlugin｣ Cannot enrich. Plugin is not usable (document: undefined).'
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

    it('when unusable, should not enrich and not log', () => {
      const testRootLocationContextFromURLPlugin = new RootLocationContextFromURLPlugin();
      testRootLocationContextFromURLPlugin.enrich(
        new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() })
      );
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
