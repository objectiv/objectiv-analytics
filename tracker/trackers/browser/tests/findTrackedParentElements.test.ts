import { isCustomParentTrackedElement, isTrackedElement, TrackingAttribute } from '../src';
import findTrackedParentElements from '../src/tracker/findTrackedParentElements';

describe('findTrackedParentElements', () => {
  afterEach(() => {
    document.getElementsByTagName('html')[0].innerHTML = '';
  });

  it('should exit immediately when an invalid Element is passed', () => {
    expect(findTrackedParentElements(null)).toHaveLength(0);
    // @ts-ignore
    expect(findTrackedParentElements(undefined)).toHaveLength(0);
    // @ts-ignore
    expect(findTrackedParentElements(0)).toHaveLength(0);
    // @ts-ignore
    expect(findTrackedParentElements(false)).toHaveLength(0);
    // @ts-ignore
    expect(findTrackedParentElements(true)).toHaveLength(0);
  });

  it('should exit immediately when the given Element is not Tracked', () => {
    const div = document.createElement('div');
    const button = document.createElement('button');
    const link = document.createElement('link');
    expect(isTrackedElement(div)).toBe(false);
    expect(isTrackedElement(button)).toBe(false);
    expect(isTrackedElement(link)).toBe(false);

    expect(findTrackedParentElements(div)).toHaveLength(0);
    expect(findTrackedParentElements(button)).toHaveLength(0);
    expect(findTrackedParentElements(link)).toHaveLength(0);
  });

  it('should return with only the given Tracked Element when it has no parents', () => {
    const div = document.createElement('div');
    div.setAttribute(TrackingAttribute.context, 'value');
    expect(isTrackedElement(div)).toBe(true);

    const trackedParentElements = findTrackedParentElements(div);
    expect(trackedParentElements).toHaveLength(1);
    expect(trackedParentElements).toStrictEqual([div]);
  });

  it('should return a list of Tracked Elements matching the DOM tree order', () => {
    const div = document.createElement('div');
    div.setAttribute(TrackingAttribute.context, 'div');

    const midSection = document.createElement('section');
    midSection.setAttribute(TrackingAttribute.context, 'mid');

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');
    topSection.setAttribute(TrackingAttribute.context, 'top');

    expect(isTrackedElement(div)).toBe(true);
    expect(isTrackedElement(midSection)).toBe(true);
    expect(isTrackedElement(untrackedSection)).toBe(false);
    expect(isTrackedElement(topSection)).toBe(true);

    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);
    document.body.appendChild(topSection);

    const trackedParentElements = findTrackedParentElements(div);
    expect(trackedParentElements).toHaveLength(3);
    expect(trackedParentElements).toStrictEqual([div, midSection, topSection]);
  });

  it('should return a list of Tracked Elements ignoring the DOM tree order and following the parentElementId', () => {
    const div = document.createElement('div');
    div.setAttribute(TrackingAttribute.context, 'div');
    div.setAttribute(TrackingAttribute.parentElementId, 'top');

    const midSection = document.createElement('section');
    midSection.setAttribute(TrackingAttribute.context, 'mid');

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');
    topSection.setAttribute(TrackingAttribute.context, 'top');
    topSection.setAttribute(TrackingAttribute.elementId, 'top');

    expect(isCustomParentTrackedElement(div)).toBe(true);
    expect(isTrackedElement(midSection)).toBe(true);
    expect(isTrackedElement(untrackedSection)).toBe(false);
    expect(isTrackedElement(topSection)).toBe(true);

    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);
    document.body.appendChild(topSection);

    const trackedParentElements = findTrackedParentElements(div);
    expect(trackedParentElements).toHaveLength(2);
    expect(trackedParentElements).toStrictEqual([div, topSection]);
  });

  it('should console.error and exit early if parentElementId is not a Tracked Element', () => {
    jest.spyOn(global.console, 'error');

    const div = document.createElement('div');
    div.setAttribute(TrackingAttribute.context, 'div');
    div.setAttribute(TrackingAttribute.parentElementId, 'top');

    const midSection = document.createElement('section');
    midSection.setAttribute(TrackingAttribute.context, 'mid');

    const untrackedSection = document.createElement('div');

    const topSection = document.createElement('body');

    expect(isCustomParentTrackedElement(div)).toBe(true);
    expect(isTrackedElement(midSection)).toBe(true);
    expect(isTrackedElement(untrackedSection)).toBe(false);
    expect(isTrackedElement(topSection)).toBe(false);

    midSection.appendChild(div);
    untrackedSection.appendChild(midSection);
    topSection.appendChild(untrackedSection);
    document.body.appendChild(topSection);

    const trackedParentElements = findTrackedParentElements(div);
    expect(trackedParentElements).toHaveLength(1);
    expect(trackedParentElements).toStrictEqual([div]);
    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenCalledWith(`findTrackedParentElements: missing or invalid Parent Element 'top'`);
  });
});
