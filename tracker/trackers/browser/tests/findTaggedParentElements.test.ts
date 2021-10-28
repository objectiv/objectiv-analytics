import { isCustomParentTaggedElement, isTaggedElement, TaggingAttribute } from '../src';
import { findTaggedParentElements } from '../src/tracker/findTaggedParentElements';

describe('findTaggedParentElements', () => {
  afterEach(() => {
    document.getElementsByTagName('html')[0].innerHTML = '';
  });

  it('should exit immediately when an invalid Element is passed', () => {
    expect(findTaggedParentElements(null)).toHaveLength(0);
    // @ts-ignore
    expect(findTaggedParentElements(undefined)).toHaveLength(0);
    // @ts-ignore
    expect(findTaggedParentElements(0)).toHaveLength(0);
    // @ts-ignore
    expect(findTaggedParentElements(false)).toHaveLength(0);
    // @ts-ignore
    expect(findTaggedParentElements(true)).toHaveLength(0);
  });

  it('should exit immediately when the given Element is not Tracked', () => {
    const div = document.createElement('div');
    const button = document.createElement('button');
    const link = document.createElement('link');
    expect(isTaggedElement(div)).toBe(false);
    expect(isTaggedElement(button)).toBe(false);
    expect(isTaggedElement(link)).toBe(false);

    expect(findTaggedParentElements(div)).toHaveLength(0);
    expect(findTaggedParentElements(button)).toHaveLength(0);
    expect(findTaggedParentElements(link)).toHaveLength(0);
  });

  it('should return with only the given Tracked Element when it has no parents', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, 'value');
    expect(isTaggedElement(div)).toBe(true);

    const trackedParentElements = findTaggedParentElements(div);
    expect(trackedParentElements).toHaveLength(1);
    expect(trackedParentElements).toStrictEqual([div]);
  });

  it('should return a list of Tracked Elements matching the DOM tree order', () => {
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

    const trackedParentElements = findTaggedParentElements(div);
    expect(trackedParentElements).toHaveLength(3);
    expect(trackedParentElements).toStrictEqual([div, midSection, topSection]);
  });

  it('should return a list of Tracked Elements ignoring the DOM tree order and following the parentElementId', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, 'div');
    div.setAttribute(TaggingAttribute.parentElementId, 'top');

    const midSection = document.createElement('section');
    midSection.setAttribute(TaggingAttribute.context, 'mid');

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');
    topSection.setAttribute(TaggingAttribute.context, 'top');
    topSection.setAttribute(TaggingAttribute.elementId, 'top');

    expect(isCustomParentTaggedElement(div)).toBe(true);
    expect(isTaggedElement(midSection)).toBe(true);
    expect(isTaggedElement(untrackedSection)).toBe(false);
    expect(isTaggedElement(topSection)).toBe(true);

    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);
    document.body.appendChild(topSection);

    const trackedParentElements = findTaggedParentElements(div);
    expect(trackedParentElements).toHaveLength(2);
    expect(trackedParentElements).toStrictEqual([div, topSection]);
  });

  it('should console.error and exit early if parentElementId is not a Tracked Element', () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});

    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.context, 'div');
    div.setAttribute(TaggingAttribute.parentElementId, 'top');

    const midSection = document.createElement('section');
    midSection.setAttribute(TaggingAttribute.context, 'mid');

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');

    expect(isCustomParentTaggedElement(div)).toBe(true);
    expect(isTaggedElement(midSection)).toBe(true);
    expect(isTaggedElement(untrackedSection)).toBe(false);
    expect(isTaggedElement(topSection)).toBe(false);

    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);
    document.body.appendChild(topSection);

    const trackedParentElements = findTaggedParentElements(div);
    expect(trackedParentElements).toHaveLength(1);
    expect(trackedParentElements).toStrictEqual([div]);
    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenCalledWith(`findTaggedParentElements: missing or invalid Parent Element 'top'`);
  });
});
