/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { makeContentContext } from '@objectiv/tracker-core';
import {
  ChildrenTaggingQueries,
  parseJson,
  parseLocationContext,
  parseTagChildren,
  parseTrackClicks,
  parseTrackVisibility,
  parseValidate,
  stringifyLocationContext,
  stringifyTagChildren,
  stringifyTrackVisibility,
  stringifyValidate,
  tagContent,
  TrackClicksAttribute,
  TrackClicksOptions,
  TrackVisibilityAttribute,
  ValidateAttribute,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('parsersAndStringifiers', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  describe('Location Contexts', () => {
    it('Should stringify and parse Section Context', () => {
      const context = makeContentContext({ id: 'test' });
      const stringifiedElementContext = stringifyLocationContext(context);
      expect(stringifiedElementContext).toStrictEqual(JSON.stringify(context));

      const parsedElementContext = parseLocationContext(stringifiedElementContext);
      expect(parsedElementContext).toStrictEqual(context);
    });

    it('Should not stringify objects that are not Location Contexts', () => {
      // @ts-ignore
      expect(() => stringifyLocationContext({ id: 'not a location context' })).toThrow();
      // @ts-ignore
      expect(() => stringifyLocationContext({})).toThrow();
    });

    it('Should not parse objects that are not stringified Location Contexts', () => {
      expect(() => parseLocationContext(`{ "id": "not a location context" }`)).toThrow();
    });

    it('Should not parse objects that are invalid Location Contexts', () => {
      expect(() => parseLocationContext(`{ "_type": "Nope", "id": "fake-news" }`)).toThrow();
    });
  });

  describe('Visibility Tagging Attribute', () => {
    it('Should stringify and parse Visibility:auto Attributes', () => {
      const visibilityAuto: TrackVisibilityAttribute = { mode: 'auto' };
      const stringifiedVisibilityAuto = stringifyTrackVisibility(visibilityAuto);
      expect(stringifiedVisibilityAuto).toStrictEqual(JSON.stringify(visibilityAuto));

      const parsedVisibilityAuto = parseTrackVisibility(stringifiedVisibilityAuto);
      expect(parsedVisibilityAuto).toStrictEqual(visibilityAuto);

      const parsedVisibilityAuto2 = parseTrackVisibility('true');
      expect(parsedVisibilityAuto2).toStrictEqual(visibilityAuto);
    });

    it('Should parse false as undefined', () => {
      const parsedVisibilityAuto2 = parseTrackVisibility('false');
      expect(parsedVisibilityAuto2).toBeUndefined();
    });

    it('Should stringify and parse Visibility:manual:visible Attributes', () => {
      const visibilityManualVisible: TrackVisibilityAttribute = { mode: 'manual', isVisible: true };
      const stringifiedVisibilityManualVisible = stringifyTrackVisibility(visibilityManualVisible);
      expect(stringifiedVisibilityManualVisible).toStrictEqual(JSON.stringify(visibilityManualVisible));

      const parsedVisibilityManualVisible = parseTrackVisibility(stringifiedVisibilityManualVisible);
      expect(parsedVisibilityManualVisible).toStrictEqual(visibilityManualVisible);
    });

    it('Should stringify and parse Visibility:manual:hidden Attributes', () => {
      const visibilityManualHidden: TrackVisibilityAttribute = { mode: 'manual', isVisible: false };
      const stringifiedVisibilityManualHidden = stringifyTrackVisibility(visibilityManualHidden);
      expect(stringifiedVisibilityManualHidden).toStrictEqual(JSON.stringify(visibilityManualHidden));

      const parsedVisibilityManualHidden = parseTrackVisibility(stringifiedVisibilityManualHidden);
      expect(parsedVisibilityManualHidden).toStrictEqual(visibilityManualHidden);
    });

    it('Should not stringify objects that are not Visibility Attributes objects or invalid ones', () => {
      // @ts-ignore
      expect(() => stringifyTrackVisibility('string')).toThrow();
      // @ts-ignore
      expect(() => stringifyTrackVisibility({ mode: 'nope' })).toThrow();
      // @ts-ignore
      expect(() => stringifyTrackVisibility({ mode: 'auto', isVisible: true })).toThrow();
      // @ts-ignore
      expect(() => stringifyTrackVisibility({ mode: 'auto', isVisible: 0 })).toThrow();
      // @ts-ignore
      expect(() => stringifyTrackVisibility({ mode: 'manual' })).toThrow();
    });

    it('Should not parse strings that are not Visibility Attributes or malformed', () => {
      // @ts-ignore
      expect(() => parseTrackVisibility('{"mode":auto}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibility('{"mode":"auto","isVisible":true}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibility('{"mode":"auto","isVisible":false}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibility('{"mode":"manual"}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibility('{"mode":"manual","isVisible":0}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibility('{"mode":"manual","isVisible":1}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibility('{"mode":"manual","isVisible":null}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibility('{"mode":"manual","isVisible":"true"}')).toThrow();
    });
  });

  describe('Validate Attribute', () => {
    it('Should parse to { locationUniqueness: true } by default', () => {
      const parsedValidateEmptyObject = parseValidate('');
      expect(parsedValidateEmptyObject).toStrictEqual({ locationUniqueness: true });

      const parsedValidateNull = parseValidate(null);
      expect(parsedValidateNull).toStrictEqual({ locationUniqueness: true });
    });

    it('Should stringify locationUniqueness as expected', () => {
      const validateLocationFalse: ValidateAttribute = { locationUniqueness: false };
      const stringifiedValidateLocationFalse = stringifyValidate(validateLocationFalse);
      expect(stringifiedValidateLocationFalse).toStrictEqual(JSON.stringify(validateLocationFalse));

      const validateLocationTrue: ValidateAttribute = { locationUniqueness: true };
      const stringifiedValidateLocationTrue = stringifyValidate(validateLocationTrue);
      expect(stringifiedValidateLocationTrue).toStrictEqual(JSON.stringify(validateLocationTrue));
    });

    it('Should not stringify objects that are not Validate Attributes objects or invalid ones', () => {
      // @ts-ignore
      expect(() => stringifyValidate('string')).toThrow();
      // @ts-ignore
      expect(() => stringifyValidate(true)).toThrow();
      // @ts-ignore
      expect(() => stringifyValidate({})).toThrow();
      // @ts-ignore
      expect(() => stringifyValidate({ locationUniqueness: 'what' })).toThrow();
      // @ts-ignore
      expect(() => stringifyValidate({ locationUniqueness: undefined })).toThrow();
      // @ts-ignore
      expect(() => stringifyValidate({ locationUniqueness: null })).toThrow();
    });

    it('Should parse validate Attributes correctly', () => {
      expect(parseValidate('{"locationUniqueness": false}')).toEqual({ locationUniqueness: false });
      expect(parseValidate('{"locationUniqueness": true}')).toEqual({ locationUniqueness: true });
    });

    it('Should not parse strings that are not validate Attributes or malformed', () => {
      // @ts-ignore
      expect(() => parseValidate('{"whatIsThis":true}')).toThrow();
      // @ts-ignore
      expect(() => parseValidate('{"locationUniqueness":"wrong"}')).toThrow();
      // @ts-ignore
      expect(() => parseValidate('{"locationUniqueness":"false"}')).toThrow();
      // @ts-ignore
      expect(() => parseValidate('{"locationUniqueness":1}')).toThrow();
      // @ts-ignore
      expect(() => parseValidate('{"locationUniqueness":null}')).toThrow();
    });
  });

  describe('Children Tagging Attribute', () => {
    it('Should stringify and parse empty Children Attributes', () => {
      const stringifiedEmptyChildren = stringifyTagChildren([]);
      expect(stringifiedEmptyChildren).toStrictEqual('[]');

      const parsedEmptyChildren = parseTagChildren(stringifiedEmptyChildren);
      expect(parsedEmptyChildren).toStrictEqual([]);
    });

    it('Should stringify and parse Children Attributes', () => {
      const elementTaggingAttributes = tagContent({ id: 'test' });
      const children: ChildrenTaggingQueries = [
        {
          queryAll: '#id',
          tagAs: elementTaggingAttributes,
        },
      ];
      const stringifiedChildren = stringifyTagChildren(children);
      expect(stringifiedChildren).toStrictEqual(
        JSON.stringify([
          {
            queryAll: '#id',
            tagAs: elementTaggingAttributes,
          },
        ])
      );

      const parsedChildren = parseTagChildren(stringifiedChildren);
      expect(parsedChildren).toStrictEqual(
        children?.map((childQuery) => ({
          ...childQuery,
          tagAs: {
            ...childQuery.tagAs,
          },
        }))
      );
    });

    it('Should not stringify objects that are not Children Attributes objects or invalid ones', () => {
      // @ts-ignore
      expect(() => stringifyTagChildren('string')).toThrow();
      // @ts-ignore
      expect(() => stringifyTagChildren(true)).toThrow();
      // @ts-ignore
      expect(() => stringifyTagChildren([null, 1, 2, 3])).toThrow();
      // @ts-ignore
      expect(() => stringifyTagChildren([undefined])).toThrow();
      // @ts-ignore
      expect(() => stringifyTagChildren([true])).toThrow();
      // @ts-ignore
      expect(() => stringifyTagChildren([false])).toThrow();
      // @ts-ignore
      expect(() => stringifyTagChildren([{}])).toThrow();
      // @ts-ignore
      expect(() => stringifyTagChildren([{ queryAll: '#id' }])).toThrow();
      // @ts-ignore
      expect(() => stringifyTagChildren([{ queryAll: '#id', tagAs: 'invalid' }])).toThrow();
    });

    it('Should not parse strings that are not Visibility Attributes or malformed', () => {
      // @ts-ignore
      expect(() => parseTagChildren()).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren(null)).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren(undefined)).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren(true)).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren(false)).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren(0)).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren(1)).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('undefined')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('null')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('true')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('false')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('0')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('1')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('{}')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('[[]]')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('[null]')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('[true]')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('[false]')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('[0]')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('[1]')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('[{}]')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('[[]]')).toThrow();
      // @ts-ignore
      expect(() => parseTagChildren('[{]')).toThrow();
    });
  });

  describe('Track Clicks Attribute to Options parsing', () => {
    const trackClicksTestCases: {
      attribute: TrackClicksAttribute;
      options: TrackClicksOptions;
    }[] = [
      {
        attribute: false,
        options: undefined,
      },
      {
        attribute: true,
        options: {},
      },
      {
        attribute: { waitUntilTracked: true },
        options: { waitForQueue: {}, flushQueue: true },
      },
      {
        attribute: { waitUntilTracked: { timeoutMs: 1 } },
        options: { waitForQueue: { timeoutMs: 1 }, flushQueue: true },
      },
      {
        attribute: { waitUntilTracked: { intervalMs: 2 } },
        options: { waitForQueue: { intervalMs: 2 }, flushQueue: true },
      },
      {
        attribute: { waitUntilTracked: { timeoutMs: 3, intervalMs: 4 } },
        options: { waitForQueue: { timeoutMs: 3, intervalMs: 4 }, flushQueue: true },
      },
      {
        attribute: { waitUntilTracked: { flushQueue: true } },
        options: { waitForQueue: {}, flushQueue: true },
      },
      {
        attribute: { waitUntilTracked: { flushQueue: false } },
        options: { waitForQueue: {}, flushQueue: false },
      },
      {
        attribute: { waitUntilTracked: { flushQueue: 'onTimeout' } },
        options: { waitForQueue: {}, flushQueue: 'onTimeout' },
      },
    ];

    trackClicksTestCases.forEach((testCase) => {
      it(`parses \`${JSON.stringify(testCase.attribute)}\` to \`${JSON.stringify(testCase.options)}\``, () => {
        const trackClicks: TrackClicksAttribute = testCase.attribute;
        const stringifiedTrackClicks = JSON.stringify(trackClicks);

        const trackClickOptions = parseTrackClicks(stringifiedTrackClicks);

        expect(trackClickOptions).toStrictEqual(testCase.options);
      });
    });

    it(`should throw`, () => {
      const stringifiedTrackClicks = JSON.stringify('{not: "valid"}');

      expect(() => parseTrackClicks(stringifiedTrackClicks)).toThrow();
    });
  });

  describe('JSON edge cases', () => {
    it('Should return null', () => {
      expect(parseJson(null)).toBeNull();
    });
  });
});
