import { isChildrenTrackingElement, isCustomParentTrackedElement, TrackingAttribute } from '../src';
import { isTrackableElement, isTrackedElement } from '../src/typeGuards';

describe('isTrackableElement', () => {
  it('should return false', () => {
    expect(isTrackableElement(document.createComment('some comment'))).toBe(false);
    expect(isTrackableElement(document.createTextNode('some text'))).toBe(false);
    expect(isTrackableElement(document.createDocumentFragment())).toBe(false);

    // TODO cover negative cases
  });

  it('should return true', () => {
    // Some HTMLElements
    expect(isTrackableElement(document.createElement('html'))).toBe(true);
    expect(isTrackableElement(document.createElement('head'))).toBe(true);
    expect(isTrackableElement(document.createElement('body'))).toBe(true);
    expect(isTrackableElement(document.createElement('title'))).toBe(true);
    expect(isTrackableElement(document.createElement('h1'))).toBe(true);
    expect(isTrackableElement(document.createElement('h2'))).toBe(true);
    expect(isTrackableElement(document.createElement('h3'))).toBe(true);
    expect(isTrackableElement(document.createElement('h4'))).toBe(true);
    expect(isTrackableElement(document.createElement('h5'))).toBe(true);
    expect(isTrackableElement(document.createElement('h6'))).toBe(true);
    expect(isTrackableElement(document.createElement('p'))).toBe(true);
    expect(isTrackableElement(document.createElement('em'))).toBe(true);
    expect(isTrackableElement(document.createElement('i'))).toBe(true);
    expect(isTrackableElement(document.createElement('b'))).toBe(true);
    expect(isTrackableElement(document.createElement('small'))).toBe(true);
    expect(isTrackableElement(document.createElement('strong'))).toBe(true);
    expect(isTrackableElement(document.createElement('u'))).toBe(true);
    expect(isTrackableElement(document.createElement('strike'))).toBe(true);
    expect(isTrackableElement(document.createElement('div'))).toBe(true);
    expect(isTrackableElement(document.createElement('button'))).toBe(true);
    expect(isTrackableElement(document.createElement('a'))).toBe(true);
    expect(isTrackableElement(document.createElement('section'))).toBe(true);
    expect(isTrackableElement(document.createElement('header'))).toBe(true);
    expect(isTrackableElement(document.createElement('nav'))).toBe(true);
    expect(isTrackableElement(document.createElement('main'))).toBe(true);
    expect(isTrackableElement(document.createElement('aside'))).toBe(true);
    expect(isTrackableElement(document.createElement('footer'))).toBe(true);
    expect(isTrackableElement(document.createElement('article'))).toBe(true);
    expect(isTrackableElement(document.createElement('ul'))).toBe(true);
    expect(isTrackableElement(document.createElement('li'))).toBe(true);
    expect(isTrackableElement(document.createElement('ol'))).toBe(true);
    expect(isTrackableElement(document.createElement('br'))).toBe(true);
    expect(isTrackableElement(document.createElement('hr'))).toBe(true);

    // Some SVGElements
    expect(isTrackableElement(document.createElement('circle'))).toBe(true);
    expect(isTrackableElement(document.createElement('line'))).toBe(true);
    expect(isTrackableElement(document.createElement('area'))).toBe(true);

    // TODO cover negative cases
  });
});

describe('isTrackedElement', () => {
  const div = document.createElement('div');
  const section = document.createElement('section');
  const button = document.createElement('button');

  it('should return false', () => {
    expect(isTrackedElement(div)).toBe(false);
    expect(isTrackedElement(section)).toBe(false);
    expect(isTrackedElement(button)).toBe(false);

    // TODO cover negative cases
  });

  it('should return true', () => {
    div.setAttribute(TrackingAttribute.context, 'value');
    expect(isTrackedElement(div)).toBe(true);

    section.setAttribute(TrackingAttribute.context, 'value');
    expect(isTrackedElement(section)).toBe(true);

    button.setAttribute(TrackingAttribute.context, 'value');
    expect(isTrackedElement(button)).toBe(true);

    // TODO cover negative cases
  });
});

describe('isChildrenTrackingElement', () => {
  const div = document.createElement('div');
  const section = document.createElement('section');
  const button = document.createElement('button');

  it('should return false', () => {
    expect(isTrackedElement(div)).toBe(false);
    expect(isTrackedElement(section)).toBe(false);
    expect(isTrackedElement(button)).toBe(false);

    // TODO cover negative cases
  });

  it('should return true', () => {
    div.setAttribute(TrackingAttribute.trackChildren, '1');
    expect(isChildrenTrackingElement(div)).toBe(true);

    section.setAttribute(TrackingAttribute.trackChildren, 'value');
    expect(isChildrenTrackingElement(section)).toBe(true);

    button.setAttribute(TrackingAttribute.trackChildren, 'value');
    expect(isChildrenTrackingElement(button)).toBe(true);

    // TODO cover negative cases
  });
});

describe('isCustomParentTrackedElement', () => {
  const div = document.createElement('div');
  const section = document.createElement('section');
  const button = document.createElement('button');

  it('should return false', () => {
    expect(isTrackedElement(div)).toBe(false);
    expect(isTrackedElement(section)).toBe(false);
    expect(isTrackedElement(button)).toBe(false);

    // TODO cover negative cases
  });

  it('should return true', () => {
    div.setAttribute(TrackingAttribute.context, 'value');
    div.setAttribute(TrackingAttribute.parentElementId, 'value');
    expect(isCustomParentTrackedElement(div)).toBe(true);

    section.setAttribute(TrackingAttribute.context, 'value');
    section.setAttribute(TrackingAttribute.parentElementId, 'value');
    expect(isCustomParentTrackedElement(section)).toBe(true);

    button.setAttribute(TrackingAttribute.context, 'value');
    button.setAttribute(TrackingAttribute.parentElementId, 'value');
    expect(isCustomParentTrackedElement(button)).toBe(true);

    // TODO cover negative cases
  });
});
