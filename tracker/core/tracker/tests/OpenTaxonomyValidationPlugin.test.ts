/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  GlobalContextName,
  LocationContextName,
  makeApplicationContext,
  makeContentContext,
  makeRootLocationContext,
  OpenTaxonomyValidationPlugin,
  Tracker,
  TrackerEvent,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

const coreTracker = new Tracker({ applicationId: 'app-id' });

describe('OpenTaxonomyValidationPlugin', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('developers tools should have been imported', async () => {
    expect(globalThis.objectiv).not.toBeUndefined();
  });

  it('should TrackerConsole.error when calling `validate` before `initialize`', () => {
    const testOpenTaxonomyValidationPlugin = new OpenTaxonomyValidationPlugin();
    const validEvent = new TrackerEvent({
      _type: 'TestEvent',
      global_contexts: [makeApplicationContext({ id: 'test' })],
      location_stack: [makeRootLocationContext({ id: 'test' })],
    });
    testOpenTaxonomyValidationPlugin.validate(validEvent);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:OpenTaxonomyValidationPlugin｣ Cannot validate. Make sure to initialize the plugin first.'
    );
  });

  describe(GlobalContextName.ApplicationContext, () => {
    it('should succeed', () => {
      const testOpenTaxonomyValidationPlugin = new OpenTaxonomyValidationPlugin();
      const validEvent = new TrackerEvent({
        _type: 'TestEvent',
        global_contexts: [makeApplicationContext({ id: 'test' })],
        location_stack: [makeRootLocationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      testOpenTaxonomyValidationPlugin.validate(validEvent);

      expect(MockConsoleImplementation.groupCollapsed).not.toHaveBeenCalled();
    });

    it('should fail when given TrackerEvent does not have ApplicationContext', () => {
      const testOpenTaxonomyValidationPlugin = new OpenTaxonomyValidationPlugin();
      testOpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithoutApplicationContext = new TrackerEvent({
        _type: 'TestEvent',
        location_stack: [makeRootLocationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      testOpenTaxonomyValidationPlugin.validate(eventWithoutApplicationContext);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:OpenTaxonomyValidationPlugin｣ Error: ApplicationContext is missing from Global Contexts of TestEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
        'color:red'
      );
    });

    it('should fail when given TrackerEvent has multiple ApplicationContexts', () => {
      const testOpenTaxonomyValidationPlugin = new OpenTaxonomyValidationPlugin();
      testOpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithDuplicatedApplicationContext = new TrackerEvent({
        _type: 'TestEvent',
        global_contexts: [makeApplicationContext({ id: 'test' }), makeApplicationContext({ id: 'test' })],
        location_stack: [makeRootLocationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      testOpenTaxonomyValidationPlugin.validate(eventWithDuplicatedApplicationContext);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:OpenTaxonomyValidationPlugin｣ Error: Only one ApplicationContext should be present in Global Contexts of TestEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
        'color:red'
      );
    });
  });

  describe(LocationContextName.RootLocationContext, () => {
    it('should succeed', () => {
      const testOpenTaxonomyValidationPlugin = new OpenTaxonomyValidationPlugin();
      testOpenTaxonomyValidationPlugin.initialize(coreTracker);
      const validEvent = new TrackerEvent({
        _type: 'TestEvent',
        location_stack: [makeRootLocationContext({ id: '/test' })],
        global_contexts: [makeApplicationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      testOpenTaxonomyValidationPlugin.validate(validEvent);

      expect(MockConsoleImplementation.groupCollapsed).not.toHaveBeenCalled();
    });

    it('should fail when given TrackerEvent does not have RootLocationContext', () => {
      const testOpenTaxonomyValidationPlugin = new OpenTaxonomyValidationPlugin();
      testOpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithoutRootLocationContext = new TrackerEvent({
        _type: 'TestEvent',
        global_contexts: [makeApplicationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      testOpenTaxonomyValidationPlugin.validate(eventWithoutRootLocationContext);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:OpenTaxonomyValidationPlugin｣ Error: RootLocationContext is missing from Location Stack of TestEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
        'color:red'
      );
    });

    it('should fail when given TrackerEvent has multiple RootLocationContexts', () => {
      const testOpenTaxonomyValidationPlugin = new OpenTaxonomyValidationPlugin();
      testOpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithDuplicatedRootLocationContext = new TrackerEvent({
        _type: 'TestEvent',
        location_stack: [makeRootLocationContext({ id: '/test' }), makeRootLocationContext({ id: '/test' })],
        global_contexts: [makeApplicationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      testOpenTaxonomyValidationPlugin.validate(eventWithDuplicatedRootLocationContext);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:OpenTaxonomyValidationPlugin｣ Error: Only one RootLocationContext should be present in Location Stack of TestEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
        'color:red'
      );
    });

    it('should fail when given TrackerEvent has a RootLocationContext in the wrong position', () => {
      const testOpenTaxonomyValidationPlugin = new OpenTaxonomyValidationPlugin();
      testOpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithRootLocationContextInWrongPosition = new TrackerEvent({
        _type: 'TestEvent',
        location_stack: [makeContentContext({ id: 'content-id' }), makeRootLocationContext({ id: '/test' })],
        global_contexts: [makeApplicationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      testOpenTaxonomyValidationPlugin.validate(eventWithRootLocationContextInWrongPosition);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:OpenTaxonomyValidationPlugin｣ Error: RootLocationContext is in the wrong position of the Location Stack of TestEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
        'color:red'
      );
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

    it('should return silently when calling `validate` before `initialize`', () => {
      const testOpenTaxonomyValidationPlugin = new OpenTaxonomyValidationPlugin();
      const validEvent = new TrackerEvent({
        _type: 'TestEvent',
        global_contexts: [makeApplicationContext({ id: 'test' })],
        location_stack: [makeRootLocationContext({ id: 'test' })],
      });
      testOpenTaxonomyValidationPlugin.validate(validEvent);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
