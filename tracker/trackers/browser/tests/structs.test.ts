import { makeSectionContext } from '@objectiv/tracker-core';
import {
  ChildrenTaggingQueries,
  parseBoolean,
  parseChildrenTaggingAttribute,
  parseLocationContext,
  parseTrackClicksAttribute,
  parseTrackVisibilityAttribute,
  stringifyBoolean,
  stringifyChildrenTaggingAttribute,
  stringifyLocationContext,
  stringifyTrackVisibilityAttribute,
  tagElement,
  TaggingAttribute,
  TrackClicksAttribute,
  TrackClicksOptions,
  TrackVisibilityAttributeAuto,
  TrackVisibilityAttributeManual,
} from '../src';

describe('Custom structs', () => {
  describe('Location Contexts', () => {
    it('Should stringify and parse Section Context', () => {
      const context = makeSectionContext({ id: 'test' });
      const stringifiedElementContext = stringifyLocationContext(context);
      expect(stringifiedElementContext).toStrictEqual(JSON.stringify(context));

      const parsedElementContext = parseLocationContext(stringifiedElementContext);
      expect(parsedElementContext).toStrictEqual(context);
    });

    it('Should not stringify objects that are not Location Contexts', () => {
      // @ts-ignore
      expect(() => stringifyLocationContext({ id: 'not a location context' })).toThrow();
    });

    it('Should not parse objects that are not stringified Location Contexts', () => {
      expect(() => parseLocationContext("{ id: 'not a location context' }")).toThrow();
    });
  });

  describe('Visibility Tagging Attribute', () => {
    it('Should stringify and parse Visibility:auto Attributes', () => {
      const visibilityAuto: TrackVisibilityAttributeAuto = { mode: 'auto' };
      const stringifiedVisibilityAuto = stringifyTrackVisibilityAttribute(visibilityAuto);
      expect(stringifiedVisibilityAuto).toStrictEqual(JSON.stringify(visibilityAuto));

      const parsedVisibilityAuto = parseTrackVisibilityAttribute(stringifiedVisibilityAuto);
      expect(parsedVisibilityAuto).toStrictEqual(visibilityAuto);
    });

    it('Should stringify and parse Visibility:manual:visible Attributes', () => {
      const visibilityManualVisible: TrackVisibilityAttributeManual = { mode: 'manual', isVisible: true };
      const stringifiedVisibilityManualVisible = stringifyTrackVisibilityAttribute(visibilityManualVisible);
      expect(stringifiedVisibilityManualVisible).toStrictEqual(JSON.stringify(visibilityManualVisible));

      const parsedVisibilityManualVisible = parseTrackVisibilityAttribute(stringifiedVisibilityManualVisible);
      expect(parsedVisibilityManualVisible).toStrictEqual(visibilityManualVisible);
    });

    it('Should stringify and parse Visibility:manual:hidden Attributes', () => {
      const visibilityManualHidden: TrackVisibilityAttributeManual = { mode: 'manual', isVisible: false };
      const stringifiedVisibilityManualHidden = stringifyTrackVisibilityAttribute(visibilityManualHidden);
      expect(stringifiedVisibilityManualHidden).toStrictEqual(JSON.stringify(visibilityManualHidden));

      const parsedVisibilityManualHidden = parseTrackVisibilityAttribute(stringifiedVisibilityManualHidden);
      expect(parsedVisibilityManualHidden).toStrictEqual(visibilityManualHidden);
    });

    it('Should not stringify objects that are not Visibility Attributes objects or invalid ones', () => {
      // @ts-ignore
      expect(() => stringifyTrackVisibilityAttribute('string')).toThrow();
      // @ts-ignore
      expect(() => stringifyTrackVisibilityAttribute(true)).toThrow();
      // @ts-ignore
      expect(() => stringifyTrackVisibilityAttribute({ mode: 'nope' })).toThrow();
      // @ts-ignore
      expect(() => stringifyTrackVisibilityAttribute({ mode: 'auto', isVisible: true })).toThrow();
      // @ts-ignore
      expect(() => stringifyTrackVisibilityAttribute({ mode: 'auto', isVisible: 0 })).toThrow();
      // @ts-ignore
      expect(() => stringifyTrackVisibilityAttribute({ mode: 'manual' })).toThrow();
    });

    it('Should not parse strings that are not Visibility Attributes or malformed', () => {
      // @ts-ignore
      expect(() => parseTrackVisibilityAttribute('{"mode":auto}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibilityAttribute('{"mode":"auto","isVisible":true}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibilityAttribute('{"mode":"auto","isVisible":false}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibilityAttribute('{"mode":"manual"}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibilityAttribute('{"mode":"manual","isVisible":0}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibilityAttribute('{"mode":"manual","isVisible":1}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibilityAttribute('{"mode":"manual","isVisible":null}')).toThrow();
      // @ts-ignore
      expect(() => parseTrackVisibilityAttribute('{"mode":"manual","isVisible":"true"}')).toThrow();
    });
  });

  describe('Booleans', () => {
    it('Should stringify and parse boolean', () => {
      expect(stringifyBoolean(true)).toBe('true');
      expect(stringifyBoolean(false)).toBe('false');
      expect(parseBoolean('true')).toBe(true);
      expect(parseBoolean('false')).toBe(false);
    });

    it('Should not stringify values that are not boolean', () => {
      // @ts-ignore
      expect(() => stringifyBoolean('True')).toThrow();
      // @ts-ignore
      expect(() => stringifyBoolean('False')).toThrow();
      // @ts-ignore
      expect(() => stringifyBoolean('string')).toThrow();
      // @ts-ignore
      expect(() => stringifyBoolean(null)).toThrow();
      // @ts-ignore
      expect(() => stringifyBoolean(undefined)).toThrow();
      // @ts-ignore
      expect(() => stringifyBoolean(0)).toThrow();
      // @ts-ignore
      expect(() => stringifyBoolean(1)).toThrow();
      // @ts-ignore
      expect(() => stringifyBoolean({})).toThrow();
      // @ts-ignore
      expect(() => stringifyBoolean([])).toThrow();
    });

    it('Should not parse values that are not boolean', () => {
      // @ts-ignore
      expect(() => parseBoolean('True')).toThrow();
      // @ts-ignore
      expect(() => parseBoolean('False')).toThrow();
      // @ts-ignore
      expect(() => parseBoolean('string')).toThrow();
      // @ts-ignore
      expect(() => parseBoolean('null')).toThrow();
      // @ts-ignore
      expect(() => parseBoolean('undefined')).toThrow();
      // @ts-ignore
      expect(() => parseBoolean('0')).toThrow();
      // @ts-ignore
      expect(() => parseBoolean('1')).toThrow();
      // @ts-ignore
      expect(() => parseBoolean('{}')).toThrow();
      // @ts-ignore
      expect(() => parseBoolean('[]')).toThrow();
      // @ts-ignore
      expect(() => parseBoolean(null)).toThrow();
      // @ts-ignore
      expect(() => parseBoolean(undefined)).toThrow();
      // @ts-ignore
      expect(() => parseBoolean(0)).toThrow();
      // @ts-ignore
      expect(() => parseBoolean(1)).toThrow();
      // @ts-ignore
      expect(() => parseBoolean({})).toThrow();
      // @ts-ignore
      expect(() => parseBoolean([])).toThrow();
    });
  });

  describe('Children Tagging Attribute', () => {
    it('Should stringify and parse empty Children Attributes', () => {
      const stringifiedEmptyChildren = stringifyChildrenTaggingAttribute([]);
      expect(stringifiedEmptyChildren).toStrictEqual('[]');

      const parsedEmptyChildren = parseChildrenTaggingAttribute(stringifiedEmptyChildren);
      expect(parsedEmptyChildren).toStrictEqual([]);
    });

    it('Should stringify and parse Children Attributes', () => {
      const elementTaggingAttributes = tagElement({ id: 'test' });
      const children: ChildrenTaggingQueries = [
        {
          queryAll: '#id',
          tagAs: elementTaggingAttributes,
        },
      ];
      const stringifiedChildren = stringifyChildrenTaggingAttribute(children);
      expect(stringifiedChildren).toStrictEqual(
        JSON.stringify([
          {
            queryAll: '#id',
            tagAs: elementTaggingAttributes,
          },
        ])
      );

      const parsedChildren = parseChildrenTaggingAttribute(stringifiedChildren);
      expect(parsedChildren).toStrictEqual(
        children?.map((childQuery) => ({
          ...childQuery,
          tagAs: {
            ...childQuery.tagAs,
            [TaggingAttribute.parentElementId]: undefined,
            [TaggingAttribute.trackBlurs]: undefined,
            [TaggingAttribute.trackClicks]: undefined,
          },
        }))
      );
    });

    it('Should not stringify objects that are not Children Attributes objects or invalid ones', () => {
      // @ts-ignore
      expect(() => stringifyChildrenAttribute('string')).toThrow();
      // @ts-ignore
      expect(() => stringifyChildrenAttribute(true)).toThrow();
      // @ts-ignore
      expect(() => stringifyChildrenAttribute([null, 1, 2, 3])).toThrow();
      // @ts-ignore
      expect(() => stringifyChildrenAttribute([undefined])).toThrow();
      // @ts-ignore
      expect(() => stringifyChildrenAttribute([true])).toThrow();
      // @ts-ignore
      expect(() => stringifyChildrenAttribute([false])).toThrow();
      // @ts-ignore
      expect(() => stringifyChildrenAttribute([{}])).toThrow();
      // @ts-ignore
      expect(() => stringifyChildrenAttribute([{ queryAll: '#id' }])).toThrow();
      // @ts-ignore
      expect(() => stringifyChildrenAttribute([{ queryAll: '#id', tagAs: 'invalid' }])).toThrow();
    });

    it('Should not parse strings that are not Visibility Attributes or malformed', () => {
      // @ts-ignore
      expect(() => parseChildrenAttribute()).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute(null)).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute(undefined)).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute(true)).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute(false)).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute(0)).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute(1)).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('undefined')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('null')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('true')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('false')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('0')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('1')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('{}')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('[[]]')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('[null]')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('[true]')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('[false]')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('[0]')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('[1]')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('[{}]')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('[[]]')).toThrow();
      // @ts-ignore
      expect(() => parseChildrenAttribute('[{]')).toThrow();
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
        attribute: { waitUntilTracked: {} },
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

        const trackClickOptions = parseTrackClicksAttribute(stringifiedTrackClicks);

        expect(trackClickOptions).toStrictEqual(testCase.options);
      });
    });
  });
});
