/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  GlobalContextName,
  LocationContextName,
  makeApplicationContext,
  makeContentContext,
  makePathContext,
  makePressEvent,
  makeRootLocationContext,
  makeSuccessEvent,
  Tracker,
  TrackerEvent,
} from '@objectiv/tracker-core';
import { OpenTaxonomyValidationPlugin } from '../src/OpenTaxonomyValidationPlugin';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

const coreTracker = new Tracker({ applicationId: 'app-id' });

describe('OpenTaxonomyValidationPlugin', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('developers tools should have been imported', async () => {
    expect(globalThis.objectiv).not.toBeUndefined();
  });

  it('should TrackerConsole.error when calling `validate` before `initialize`', () => {
    OpenTaxonomyValidationPlugin.initialized = false;
    const validEvent = new TrackerEvent({
      _type: 'TestEvent',
      global_contexts: [makeApplicationContext({ id: 'test' })],
      location_stack: [makeRootLocationContext({ id: 'test' })],
    });
    OpenTaxonomyValidationPlugin.validate(validEvent);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:OpenTaxonomyValidationPlugin｣ Cannot validate. Make sure to initialize the plugin first.'
    );
  });

  describe(GlobalContextName.ApplicationContext, () => {
    it('should succeed', () => {
      const validEvent = new TrackerEvent({
        _type: 'TestEvent',
        global_contexts: [makeApplicationContext({ id: 'test' })],
        location_stack: [makeRootLocationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      OpenTaxonomyValidationPlugin.validate(validEvent);

      expect(MockConsoleImplementation.groupCollapsed).not.toHaveBeenCalled();
    });

    it('should fail when given TrackerEvent does not have ApplicationContext', () => {
      OpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithoutApplicationContext = new TrackerEvent({
        _type: 'TestEvent',
        location_stack: [makeRootLocationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      OpenTaxonomyValidationPlugin.validate(eventWithoutApplicationContext);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:OpenTaxonomyValidationPlugin｣ Error: ApplicationContext is missing from Global Contexts of TestEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
        'color:red'
      );
    });

    it('should fail when given TrackerEvent has multiple ApplicationContexts', () => {
      OpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithDuplicatedApplicationContext = new TrackerEvent({
        _type: 'TestEvent',
        global_contexts: [makeApplicationContext({ id: 'test' }), makeApplicationContext({ id: 'test' })],
        location_stack: [makeRootLocationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      OpenTaxonomyValidationPlugin.validate(eventWithDuplicatedApplicationContext);

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
      OpenTaxonomyValidationPlugin.initialize(coreTracker);
      const validEvent = new TrackerEvent({
        _type: 'TestEvent',
        location_stack: [makeRootLocationContext({ id: '/test' })],
        global_contexts: [makeApplicationContext({ id: 'test' })],
      });

      jest.resetAllMocks();

      OpenTaxonomyValidationPlugin.validate(validEvent);

      expect(MockConsoleImplementation.groupCollapsed).not.toHaveBeenCalled();
    });

    it('should allow non-interactive Events without RootLocationContext and PathContext', () => {
      OpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithoutRootLocationContext = new TrackerEvent(
        makeSuccessEvent({
          message: ' ok',
          global_contexts: [makeApplicationContext({ id: 'test' })],
        })
      );

      jest.resetAllMocks();

      OpenTaxonomyValidationPlugin.validate(eventWithoutRootLocationContext);

      expect(MockConsoleImplementation.groupCollapsed).not.toHaveBeenCalled();
    });

    it('should fail when given TrackerEvent does not have RootLocationContext', () => {
      OpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithoutRootLocationContext = new TrackerEvent(
        makePressEvent({
          global_contexts: [makeApplicationContext({ id: 'test' }), makePathContext({ id: '/path' })],
        })
      );

      jest.resetAllMocks();

      OpenTaxonomyValidationPlugin.validate(eventWithoutRootLocationContext);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:OpenTaxonomyValidationPlugin｣ Error: RootLocationContext is missing from Location Stack of PressEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
        'color:red'
      );
    });

    it('should fail when given TrackerEvent has multiple RootLocationContexts', () => {
      OpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithDuplicatedRootLocationContext = new TrackerEvent(
        makePressEvent({
          location_stack: [makeRootLocationContext({ id: '/test' }), makeRootLocationContext({ id: '/test' })],
          global_contexts: [makeApplicationContext({ id: 'test' }), makePathContext({ id: '/path' })],
        })
      );

      jest.resetAllMocks();

      OpenTaxonomyValidationPlugin.validate(eventWithDuplicatedRootLocationContext);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:OpenTaxonomyValidationPlugin｣ Error: Only one RootLocationContext should be present in Location Stack of PressEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
        'color:red'
      );
    });

    it('should fail when given TrackerEvent has a RootLocationContext in the wrong position', () => {
      OpenTaxonomyValidationPlugin.initialize(coreTracker);
      const eventWithRootLocationContextInWrongPosition = new TrackerEvent(
        makePressEvent({
          location_stack: [makeContentContext({ id: 'content-id' }), makeRootLocationContext({ id: '/test' })],
          global_contexts: [makeApplicationContext({ id: 'test' }), makePathContext({ id: '/path' })],
        })
      );

      jest.resetAllMocks();

      OpenTaxonomyValidationPlugin.validate(eventWithRootLocationContextInWrongPosition);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:OpenTaxonomyValidationPlugin｣ Error: RootLocationContext is in the wrong position of the Location Stack of PressEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
        'color:red'
      );
    });
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

    it('should return silently when calling `validate` before `initialize`', () => {
      const validEvent = new TrackerEvent({
        _type: 'TestEvent',
        global_contexts: [makeApplicationContext({ id: 'test' })],
        location_stack: [makeRootLocationContext({ id: 'test' })],
      });
      OpenTaxonomyValidationPlugin.validate(validEvent);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
