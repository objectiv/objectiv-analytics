/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  generateUUID,
  GlobalContextName,
  LocationContextName,
  TrackerEvent,
  TrackerPlatform,
} from '@objectiv/tracker-core';
import { TrackerConsole } from '../src/TrackerConsole';
import { makeGlobalContextValidationRule } from '../src/validationRules/makeGlobalContextValidationRule';
import { makeLocationContextValidationRule } from '../src/validationRules/makeLocationContextValidationRule';

TrackerConsole.setImplementation(MockConsoleImplementation);

describe('Validation Rules', () => {
  describe('GlobalContextValidationRules', () => {
    it('Should TrackerConsole.error if given contextName is missing', () => {
      const testGlobalContextValidationRule = makeGlobalContextValidationRule({
        platform: TrackerPlatform.CORE,
        contextName: GlobalContextName.PathContext,
      });

      jest.resetAllMocks();

      testGlobalContextValidationRule.validate(new TrackerEvent({ _type: 'PressEvent' }));

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledWith(
        '%c｢objectiv｣ Error: PathContext is missing from Global Contexts of PressEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
        'color:red'
      );
    });

    it('Should prefix TrackerConsole.error messages with logPrefix', () => {
      const testGlobalContextValidationRule = makeGlobalContextValidationRule({
        platform: TrackerPlatform.CORE,
        contextName: GlobalContextName.PathContext,
        logPrefix: 'TestPrefix',
      });

      jest.resetAllMocks();

      testGlobalContextValidationRule.validate(new TrackerEvent({ _type: 'PressEvent' }));

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledWith(
        '%c｢objectiv:TestPrefix｣ Error: PathContext is missing from Global Contexts of PressEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
        'color:red'
      );
    });

    it('Should TrackerConsole.error if given contextName is present more than once', () => {
      const testGlobalContextValidationRule = makeGlobalContextValidationRule({
        platform: TrackerPlatform.CORE,
        contextName: GlobalContextName.PathContext,
        once: true,
      });

      jest.resetAllMocks();

      testGlobalContextValidationRule.validate(
        new TrackerEvent({
          _type: 'PressEvent',
          global_contexts: [
            { __instance_id: generateUUID(), __global_context: true, _type: GlobalContextName.PathContext, id: 'test' },
            { __instance_id: generateUUID(), __global_context: true, _type: GlobalContextName.PathContext, id: 'test' },
          ],
        })
      );

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledWith(
        '%c｢objectiv｣ Error: Only one PathContext should be present in Global Contexts of PressEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
        'color:red'
      );
    });
  });

  describe('LocationContextValidationRules', () => {
    it('Should TrackerConsole.error if given contextName is missing', () => {
      const testLocationContextValidationRule = makeLocationContextValidationRule({
        platform: TrackerPlatform.CORE,
        contextName: LocationContextName.ContentContext,
      });

      jest.resetAllMocks();

      testLocationContextValidationRule.validate(new TrackerEvent({ _type: 'PressEvent' }));

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledWith(
        '%c｢objectiv｣ Error: ContentContext is missing from Location Stack of PressEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
        'color:red'
      );
    });

    it('Should prefix TrackerConsole.error messages with logPrefix', () => {
      const testLocationContextValidationRule = makeLocationContextValidationRule({
        platform: TrackerPlatform.CORE,
        contextName: LocationContextName.ContentContext,
        logPrefix: 'TestPrefix',
      });

      jest.resetAllMocks();

      testLocationContextValidationRule.validate(new TrackerEvent({ _type: 'PressEvent' }));

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledWith(
        '%c｢objectiv:TestPrefix｣ Error: ContentContext is missing from Location Stack of PressEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
        'color:red'
      );
    });

    it('Should TrackerConsole.error if given contextName is present more than once', () => {
      const testLocationContextValidationRule = makeLocationContextValidationRule({
        platform: TrackerPlatform.CORE,
        contextName: LocationContextName.ContentContext,
        once: true,
      });

      jest.resetAllMocks();

      testLocationContextValidationRule.validate(
        new TrackerEvent({
          _type: 'PressEvent',
          location_stack: [
            {
              __instance_id: generateUUID(),
              __location_context: true,
              _type: LocationContextName.ContentContext,
              id: 'test',
            },
            {
              __instance_id: generateUUID(),
              __location_context: true,
              _type: LocationContextName.ContentContext,
              id: 'test',
            },
          ],
        })
      );

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledWith(
        '%c｢objectiv｣ Error: Only one ContentContext should be present in Location Stack of PressEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
        'color:red'
      );
    });

    it('Should TrackerConsole.error if given contextName is present in the wrong position', () => {
      const testLocationContextValidationRule = makeLocationContextValidationRule({
        platform: TrackerPlatform.CORE,
        contextName: LocationContextName.ContentContext,
        once: true,
        position: 0,
      });

      jest.resetAllMocks();

      testLocationContextValidationRule.validate(
        new TrackerEvent({
          _type: 'PressEvent',
          location_stack: [
            {
              __instance_id: generateUUID(),
              __location_context: true,
              _type: LocationContextName.RootLocationContext,
              id: 'test',
            },
            {
              __instance_id: generateUUID(),
              __location_context: true,
              _type: LocationContextName.ContentContext,
              id: 'test',
            },
          ],
        })
      );

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledWith(
        '%c｢objectiv｣ Error: ContentContext is in the wrong position of the Location Stack of PressEvent.\n' +
          'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
        'color:red'
      );
    });
  });
});
