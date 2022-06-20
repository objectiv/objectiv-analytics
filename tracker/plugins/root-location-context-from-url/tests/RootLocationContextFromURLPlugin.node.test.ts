/*
 * Copyright 2021-2022 Objectiv B.V.
 * @jest-environment node
 */
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { TrackerEvent, TrackerRepository } from '@objectiv/tracker-core';
import { RootLocationContextFromURLPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('RootLocationContextFromURLPlugin - node', () => {
  beforeEach(() => {
    TrackerRepository.trackersMap.clear();
    TrackerRepository.defaultTracker = undefined;
  });

  it('should instantiate as unusable', () => {
    const testRootLocationContextFromURLPlugin = new RootLocationContextFromURLPlugin();
    expect(testRootLocationContextFromURLPlugin.isUsable()).toBe(false);
  });

  it('when unusable, should not enrich and log an error message', () => {
    const testRootLocationContextFromURLPlugin = new RootLocationContextFromURLPlugin();
    testRootLocationContextFromURLPlugin.enrich(new TrackerEvent({ _type: 'test-event' }));
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:RootLocationContextFromURLPlugin｣ Cannot enrich. Plugin is not usable (document: undefined).'
    );
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

    it('when unusable, should not enrich and not log', () => {
      const testRootLocationContextFromURLPlugin = new RootLocationContextFromURLPlugin();
      testRootLocationContextFromURLPlugin.enrich(new TrackerEvent({ _type: 'test-event' }));
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
