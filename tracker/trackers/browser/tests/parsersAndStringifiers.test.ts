/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { expectToThrow, MockConsoleImplementation } from '@objectiv/testing-tools';
import { makeContentContext } from '@objectiv/tracker-core';
import {
  ChildrenTaggingQueries,
  parseJson,
  parseLocationContext,
  parseTagChildren,
  parseTrackBlurs,
  parseTrackClicks,
  parseTrackVisibility,
  parseValidate,
  stringifyLocationContext,
  stringifyTagChildren,
  stringifyTrackVisibility,
  stringifyValidate,
  tagContent,
  TrackBlursAttribute,
  TrackBlursOptions,
  TrackClicksAttribute,
  TrackClicksOptions,
  TrackVisibilityAttribute,
  ValidateAttribute,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

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
      expectToThrow(() => stringifyLocationContext({ id: 'not a location context' }));
      // @ts-ignore
      expectToThrow(() => stringifyLocationContext({}));
    });

    it('Should not parse objects that are not stringified Location Contexts', () => {
      expectToThrow(() => parseLocationContext(`{ "id": "not a location context" }`));
    });

    it('Should not parse objects that are invalid Location Contexts', () => {
      expectToThrow(() => parseLocationContext(`{ "_type": "Nope", "id": "fake-news" }`));
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
      expectToThrow(() => stringifyTrackVisibility('string'));
      // @ts-ignore
      expectToThrow(() => stringifyTrackVisibility({ mode: 'nope' }));
      // @ts-ignore
      expectToThrow(() => stringifyTrackVisibility({ mode: 'auto', isVisible: true }));
      // @ts-ignore
      expectToThrow(() => stringifyTrackVisibility({ mode: 'auto', isVisible: 0 }));
      // @ts-ignore
      expectToThrow(() => stringifyTrackVisibility({ mode: 'manual' }));
    });

    it('Should not parse strings that are not Visibility Attributes or malformed', () => {
      // @ts-ignore
      expectToThrow(() => parseTrackVisibility('{"mode":auto}'));
      // @ts-ignore
      expectToThrow(() => parseTrackVisibility('{"mode":"auto","isVisible":true}'));
      // @ts-ignore
      expectToThrow(() => parseTrackVisibility('{"mode":"auto","isVisible":false}'));
      // @ts-ignore
      expectToThrow(() => parseTrackVisibility('{"mode":"manual"}'));
      // @ts-ignore
      expectToThrow(() => parseTrackVisibility('{"mode":"manual","isVisible":0}'));
      // @ts-ignore
      expectToThrow(() => parseTrackVisibility('{"mode":"manual","isVisible":1}'));
      // @ts-ignore
      expectToThrow(() => parseTrackVisibility('{"mode":"manual","isVisible":null}'));
      // @ts-ignore
      expectToThrow(() => parseTrackVisibility('{"mode":"manual","isVisible":"true"}'));
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
      expectToThrow(() => stringifyValidate('string'));
      // @ts-ignore
      expectToThrow(() => stringifyValidate(true));
      // @ts-ignore
      expectToThrow(() => stringifyValidate({}));
      // @ts-ignore
      expectToThrow(() => stringifyValidate({ locationUniqueness: 'what' }));
      // @ts-ignore
      expectToThrow(() => stringifyValidate({ locationUniqueness: undefined }));
      // @ts-ignore
      expectToThrow(() => stringifyValidate({ locationUniqueness: null }));
    });

    it('Should parse validate Attributes correctly', () => {
      expect(parseValidate('{"locationUniqueness": false}')).toEqual({ locationUniqueness: false });
      expect(parseValidate('{"locationUniqueness": true}')).toEqual({ locationUniqueness: true });
    });

    it('Should not parse strings that are not validate Attributes or malformed', () => {
      // @ts-ignore
      expectToThrow(() => parseValidate('{"whatIsThis":true}'));
      // @ts-ignore
      expectToThrow(() => parseValidate('{"locationUniqueness":"wrong"}'));
      // @ts-ignore
      expectToThrow(() => parseValidate('{"locationUniqueness":"false"}'));
      // @ts-ignore
      expectToThrow(() => parseValidate('{"locationUniqueness":1}'));
      // @ts-ignore
      expectToThrow(() => parseValidate('{"locationUniqueness":null}'));
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
      expectToThrow(() => stringifyTagChildren('string'));
      // @ts-ignore
      expectToThrow(() => stringifyTagChildren(true));
      // @ts-ignore
      expectToThrow(() => stringifyTagChildren([null, 1, 2, 3]));
      // @ts-ignore
      expectToThrow(() => stringifyTagChildren([undefined]));
      // @ts-ignore
      expectToThrow(() => stringifyTagChildren([true]));
      // @ts-ignore
      expectToThrow(() => stringifyTagChildren([false]));
      // @ts-ignore
      expectToThrow(() => stringifyTagChildren([{}]));
      // @ts-ignore
      expectToThrow(() => stringifyTagChildren([{ queryAll: '#id' }]));
      // @ts-ignore
      expectToThrow(() => stringifyTagChildren([{ queryAll: '#id', tagAs: 'invalid' }]));
    });

    it('Should not parse strings that are not Visibility Attributes or malformed', () => {
      // @ts-ignore
      expectToThrow(() => parseTagChildren());
      // @ts-ignore
      expectToThrow(() => parseTagChildren(null));
      // @ts-ignore
      expectToThrow(() => parseTagChildren(undefined));
      // @ts-ignore
      expectToThrow(() => parseTagChildren(true));
      // @ts-ignore
      expectToThrow(() => parseTagChildren(false));
      // @ts-ignore
      expectToThrow(() => parseTagChildren(0));
      // @ts-ignore
      expectToThrow(() => parseTagChildren(1));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('undefined'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('null'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('true'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('false'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('0'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('1'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('{}'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('[[]]'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('[null]'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('[true]'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('[false]'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('[0]'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('[1]'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('[{}]'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('[[]]'));
      // @ts-ignore
      expectToThrow(() => parseTagChildren('[{]'));
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

      expectToThrow(() => parseTrackClicks(stringifiedTrackClicks));
    });
  });

  describe('Track Blurs Attribute to Options parsing', () => {
    const trackBlursTestCases: {
      attribute: TrackBlursAttribute;
      options: TrackBlursOptions;
    }[] = [
      {
        attribute: false,
        options: undefined,
      },
      {
        attribute: true,
        options: { trackValue: false },
      },
      {
        attribute: { trackValue: true },
        options: { trackValue: true },
      },
      {
        attribute: { trackValue: false },
        options: { trackValue: false },
      },
    ];

    trackBlursTestCases.forEach((testCase) => {
      it(`parses \`${JSON.stringify(testCase.attribute)}\` to \`${JSON.stringify(testCase.options)}\``, () => {
        const trackBlurs: TrackBlursAttribute = testCase.attribute;
        const stringifiedTrackBlurs = JSON.stringify(trackBlurs);

        const trackBlursOptions = parseTrackBlurs(stringifiedTrackBlurs);

        expect(trackBlursOptions).toStrictEqual(testCase.options);
      });
    });

    it(`should throw`, () => {
      const stringifiedTrackBlursInvalid = JSON.stringify('{not: "valid"}');

      expectToThrow(() => parseTrackBlurs(stringifiedTrackBlursInvalid));

      const stringifiedTrackBlursNull = JSON.stringify(null);

      expectToThrow(() => parseTrackBlurs(stringifiedTrackBlursNull));
    });
  });

  describe('JSON edge cases', () => {
    it('Should return null', () => {
      expect(parseJson(null)).toBeNull();
    });
  });
});
