/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { findParentTaggedElements, isParentTaggedElement, isTaggedElement, TaggingAttribute } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('findTaggedParentElements', () => {
  afterEach(() => {
    document.getElementsByTagName('html')[0].innerHTML = '';
  });

  it('should exit immediately when an invalid Element is passed', () => {
    expect(findParentTaggedElements(null)).toHaveLength(0);
    // @ts-ignore
    expect(findParentTaggedElements(undefined)).toHaveLength(0);
    // @ts-ignore
    expect(findParentTaggedElements(0)).toHaveLength(0);
    // @ts-ignore
    expect(findParentTaggedElements(false)).toHaveLength(0);
    // @ts-ignore
    expect(findParentTaggedElements(true)).toHaveLength(0);
  });

  it('should exit immediately when the given Element is not Tracked', () => {
    const div = document.createElement('div');
    const button = document.createElement('button');
    const link = document.createElement('link');
    expect(isTaggedElement(div)).toBe(false);
    expect(isTaggedElement(button)).toBe(false);
    expect(isTaggedElement(link)).toBe(false);

    expect(findParentTaggedElements(div)).toHaveLength(0);
    expect(findParentTaggedElements(button)).toHaveLength(0);
    expect(findParentTaggedElements(link)).toHaveLength(0);
  });

  it('should return with only the given Tagged Element when it has no parents', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, 'value');
    expect(isTaggedElement(div)).toBe(true);

    const trackedParentElements = findParentTaggedElements(div);
    expect(trackedParentElements).toHaveLength(1);
    expect(trackedParentElements).toStrictEqual([div]);
  });

  it('should return a list of Tagged Elements matching the DOM tree order', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, 'div');

    const midSection = document.createElement('section');
    midSection.setAttribute(TaggingAttribute.context, 'mid');

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');
    topSection.setAttribute(TaggingAttribute.context, 'top');

    expect(isTaggedElement(div)).toBe(true);
    expect(isTaggedElement(midSection)).toBe(true);
    expect(isTaggedElement(untrackedSection)).toBe(false);
    expect(isTaggedElement(topSection)).toBe(true);

    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);
    document.body.appendChild(topSection);

    const trackedParentElements = findParentTaggedElements(div);
    expect(trackedParentElements).toHaveLength(3);
    expect(trackedParentElements).toStrictEqual([div, midSection, topSection]);
  });

  it('should return a list of Tagged Elements ignoring the DOM tree order and following the parentElementId', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, 'div');
    div.setAttribute(TaggingAttribute.parentElementId, 'top');

    const midSection = document.createElement('section');
    midSection.setAttribute(TaggingAttribute.context, 'mid');

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');
    topSection.setAttribute(TaggingAttribute.context, 'top');
    topSection.setAttribute(TaggingAttribute.elementId, 'top');

    expect(isParentTaggedElement(div)).toBe(true);
    expect(isTaggedElement(midSection)).toBe(true);
    expect(isTaggedElement(untrackedSection)).toBe(false);
    expect(isTaggedElement(topSection)).toBe(true);

    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);
    document.body.appendChild(topSection);

    const trackedParentElements = findParentTaggedElements(div);
    expect(trackedParentElements).toHaveLength(2);
    expect(trackedParentElements).toStrictEqual([div, topSection]);
  });

  it('should TrackerConsole.error and exit early if parentElementId is not a Tagged Element', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, 'div');
    div.setAttribute(TaggingAttribute.parentElementId, 'top');

    const midSection = document.createElement('section');
    midSection.setAttribute(TaggingAttribute.context, 'mid');

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');

    expect(isParentTaggedElement(div)).toBe(true);
    expect(isTaggedElement(midSection)).toBe(true);
    expect(isTaggedElement(untrackedSection)).toBe(false);
    expect(isTaggedElement(topSection)).toBe(false);

    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);
    document.body.appendChild(topSection);

    const trackedParentElements = findParentTaggedElements(div);
    expect(trackedParentElements).toHaveLength(1);
    expect(trackedParentElements).toStrictEqual([div]);
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      `findParentTaggedElements: missing or invalid Parent Element 'top'`
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

    it('should not TrackerConsole.error if parentElementId is not a Tagged Element', () => {
      const div = document.createElement('div');
      div.setAttribute(TaggingAttribute.context, 'div');
      div.setAttribute(TaggingAttribute.parentElementId, 'top');

      const midSection = document.createElement('section');
      midSection.setAttribute(TaggingAttribute.context, 'mid');

      const untrackedSection = document.createElement('div');

      const topSection = document.createElement('body');

      expect(isParentTaggedElement(div)).toBe(true);
      expect(isTaggedElement(midSection)).toBe(true);
      expect(isTaggedElement(untrackedSection)).toBe(false);
      expect(isTaggedElement(topSection)).toBe(false);

      midSection.appendChild(div);
      untrackedSection.appendChild(midSection);
      topSection.appendChild(untrackedSection);
      document.body.appendChild(topSection);

      const trackedParentElements = findParentTaggedElements(div);
      expect(trackedParentElements).toHaveLength(1);
      expect(trackedParentElements).toStrictEqual([div]);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
