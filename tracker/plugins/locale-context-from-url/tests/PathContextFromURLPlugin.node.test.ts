/*
 * Copyright 2022 Objectiv B.V.
 * @jest-environment node
 */
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { TrackerEvent } from '@objectiv/tracker-core';
import { LocaleContextFromURLPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('LocaleContextFromURLPlugin - node', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should instantiate as unusable', () => {
    const testLocaleContextFromURLPlugin = new LocaleContextFromURLPlugin({
      idFactoryFunction: () => location.pathname.split('/')[1] ?? null,
    });
    expect(testLocaleContextFromURLPlugin.isUsable()).toBe(false);
  });

  it('when unusable, should not enrich and log an error message', () => {
    const testLocaleContextFromURLPlugin = new LocaleContextFromURLPlugin({
      idFactoryFunction: () => location.pathname.split('/')[1] ?? null,
    });
    testLocaleContextFromURLPlugin.enrich(new TrackerEvent({ _type: 'test-event' }));
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:LocaleContextFromURLPlugin｣ Cannot enrich. Plugin is not usable (document: undefined).'
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
      new LocaleContextFromURLPlugin({
        idFactoryFunction: () => location.pathname.split('/')[1] ?? null,
      });
      expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
    });

    it('when unusable, should not enrich and not log', () => {
      const testLocaleContextFromURLPlugin = new LocaleContextFromURLPlugin({
        idFactoryFunction: () => location.pathname.split('/')[1] ?? null,
      });
      testLocaleContextFromURLPlugin.enrich(new TrackerEvent({ _type: 'test-event' }));
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should not log failure to enrich', async () => {
      const testLocaleContextFromURLPlugin = new LocaleContextFromURLPlugin({
        idFactoryFunction: () => null,
      });
      testLocaleContextFromURLPlugin.isUsable = () => true;
      testLocaleContextFromURLPlugin.enrich(new TrackerEvent({ _type: 'test-event' }));
      expect(MockConsoleImplementation.warn).not.toHaveBeenCalled();
    });
  });
});
