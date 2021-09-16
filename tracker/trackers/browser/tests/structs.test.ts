import { makeSectionContext } from '@objectiv/tracker-core';
import {
  parseBoolean,
  parseChildrenAttribute,
  parseLocationContext,
  parseVisibilityAttribute,
  stringifyBoolean,
  stringifyChildrenAttribute,
  stringifyLocationContext,
  stringifyVisibilityAttribute,
  TrackChildrenParameters,
  trackElement,
  TrackingAttribute,
  TrackingAttributeVisibilityAuto,
  TrackingAttributeVisibilityManual,
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

  describe('Visibility Tracking Attribute', () => {
    it('Should stringify and parse Visibility:auto Attributes', () => {
      const visibilityAuto: TrackingAttributeVisibilityAuto = { mode: 'auto' };
      const stringifiedVisibilityAuto = stringifyVisibilityAttribute(visibilityAuto);
      expect(stringifiedVisibilityAuto).toStrictEqual(JSON.stringify(visibilityAuto));

      const parsedVisibilityAuto = parseVisibilityAttribute(stringifiedVisibilityAuto);
      expect(parsedVisibilityAuto).toStrictEqual(visibilityAuto);
    });

    it('Should stringify and parse Visibility:manual:visible Attributes', () => {
      const visibilityManualVisible: TrackingAttributeVisibilityManual = { mode: 'manual', isVisible: true };
      const stringifiedVisibilityManualVisible = stringifyVisibilityAttribute(visibilityManualVisible);
      expect(stringifiedVisibilityManualVisible).toStrictEqual(JSON.stringify(visibilityManualVisible));

      const parsedVisibilityManualVisible = parseVisibilityAttribute(stringifiedVisibilityManualVisible);
      expect(parsedVisibilityManualVisible).toStrictEqual(visibilityManualVisible);
    });

    it('Should stringify and parse Visibility:manual:hidden Attributes', () => {
      const visibilityManualHidden: TrackingAttributeVisibilityManual = { mode: 'manual', isVisible: false };
      const stringifiedVisibilityManualHidden = stringifyVisibilityAttribute(visibilityManualHidden);
      expect(stringifiedVisibilityManualHidden).toStrictEqual(JSON.stringify(visibilityManualHidden));

      const parsedVisibilityManualHidden = parseVisibilityAttribute(stringifiedVisibilityManualHidden);
      expect(parsedVisibilityManualHidden).toStrictEqual(visibilityManualHidden);
    });

    it('Should not stringify objects that are not Visibility Attributes objects or invalid ones', () => {
      // @ts-ignore
      expect(() => stringifyVisibilityAttribute('string')).toThrow();
      // @ts-ignore
      expect(() => stringifyVisibilityAttribute(true)).toThrow();
      // @ts-ignore
      expect(() => stringifyVisibilityAttribute({ mode: 'nope' })).toThrow();
      // @ts-ignore
      expect(() => stringifyVisibilityAttribute({ mode: 'auto', isVisible: true })).toThrow();
      // @ts-ignore
      expect(() => stringifyVisibilityAttribute({ mode: 'auto', isVisible: 0 })).toThrow();
      // @ts-ignore
      expect(() => stringifyVisibilityAttribute({ mode: 'manual' })).toThrow();
    });

    it('Should not parse strings that are not Visibility Attributes or malformed', () => {
      // @ts-ignore
      expect(() => parseVisibilityAttribute('{"mode":auto}')).toThrow();
      // @ts-ignore
      expect(() => parseVisibilityAttribute('{"mode":"auto","isVisible":true}')).toThrow();
      // @ts-ignore
      expect(() => parseVisibilityAttribute('{"mode":"auto","isVisible":false}')).toThrow();
      // @ts-ignore
      expect(() => parseVisibilityAttribute('{"mode":"manual"}')).toThrow();
      // @ts-ignore
      expect(() => parseVisibilityAttribute('{"mode":"manual","isVisible":0}')).toThrow();
      // @ts-ignore
      expect(() => parseVisibilityAttribute('{"mode":"manual","isVisible":1}')).toThrow();
      // @ts-ignore
      expect(() => parseVisibilityAttribute('{"mode":"manual","isVisible":null}')).toThrow();
      // @ts-ignore
      expect(() => parseVisibilityAttribute('{"mode":"manual","isVisible":"true"}')).toThrow();
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

  describe('Children Tracking Attribute', () => {
    it('Should stringify and parse empty Children Attributes', () => {
      const stringifiedEmptyChildren = stringifyChildrenAttribute([]);
      expect(stringifiedEmptyChildren).toStrictEqual('[]');

      const parsedEmptyChildren = parseChildrenAttribute(stringifiedEmptyChildren);
      expect(parsedEmptyChildren).toStrictEqual([]);
    });

    it('Should stringify and parse Children Attributes', () => {
      const elementTrackingAttributes = trackElement({ id: 'test' });
      const children: TrackChildrenParameters = [
        {
          queryAll: '#id',
          trackAs: elementTrackingAttributes,
        },
      ];
      const stringifiedChildren = stringifyChildrenAttribute(children);
      expect(stringifiedChildren).toStrictEqual(
        JSON.stringify([
          {
            queryAll: '#id',
            trackAs: elementTrackingAttributes,
          },
        ])
      );

      const parsedChildren = parseChildrenAttribute(stringifiedChildren);
      expect(parsedChildren).toStrictEqual(
        children?.map((childQuery) => ({
          ...childQuery,
          trackAs: {
            ...childQuery.trackAs,
            [TrackingAttribute.parentElementId]: undefined,
            [TrackingAttribute.trackBlurs]: undefined,
            [TrackingAttribute.trackClicks]: undefined,
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
      expect(() => stringifyChildrenAttribute([{ queryAll: '#id', trackAs: 'invalid' }])).toThrow();
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
});
