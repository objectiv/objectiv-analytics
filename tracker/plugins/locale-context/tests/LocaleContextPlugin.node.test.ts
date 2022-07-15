/*
 * Copyright 2022 Objectiv B.V.
 * @jest-environment node
 */
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateUUID, TrackerEvent } from '@objectiv/tracker-core';
import { LocaleContextPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('LocaleContextPlugin - node', () => {
  beforeEach(() => {
    jest.resetAllMocks();
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
      new LocaleContextPlugin({
        idFactoryFunction: () => location.pathname.split('/')[1] ?? null,
      });
      expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
    });

    it('should not log failure to enrich', async () => {
      const testLocaleContextPlugin = new LocaleContextPlugin({
        idFactoryFunction: () => null,
      });
      testLocaleContextPlugin.isUsable = () => true;
      testLocaleContextPlugin.enrich(new TrackerEvent({ _type: 'test-event', id: generateUUID(), time: Date.now() }));
      expect(MockConsoleImplementation.warn).not.toHaveBeenCalled();
    });
  });
});
