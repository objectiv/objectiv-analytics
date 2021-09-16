import { makeButtonContext } from '@objectiv/tracker-core';
import { isTrackedElement, trackButton, trackElement, TrackingAttribute } from '../src';
import processChildrenTrackingElement from '../src/observer/processChildrenTrackingElement';

describe('processChildrenTrackingElement', () => {
  it('should exit with an empty array if the given Element has no children tracking attribute', () => {
    const div = document.createElement('div');

    expect(processChildrenTrackingElement(div)).toHaveLength(0);
  });

  it('should exit with an empty array if the given Element has an invalid children tracking attribute', () => {
    const div = document.createElement('div');
    div.setAttribute(TrackingAttribute.trackChildren, 'null');

    expect(processChildrenTrackingElement(div)).toHaveLength(0);
  });

  it('should exit with an empty array if the given Element has an empty list of children tracking queries', () => {
    const div = document.createElement('div');
    div.setAttribute(TrackingAttribute.trackChildren, '[]');

    expect(processChildrenTrackingElement(div)).toHaveLength(0);
  });

  it('should skip queries without trackAs', () => {
    const div = document.createElement('div');
    div.setAttribute(TrackingAttribute.trackChildren, JSON.stringify([{ queryAll: '#some-id-2', trackAs: null }]));

    expect(processChildrenTrackingElement(div)).toHaveLength(0);
  });

  it('should skip queries without valid or empty trackAs, query or queryAll options', () => {
    const div = document.createElement('div');
    div.setAttribute(
      TrackingAttribute.trackChildren,
      JSON.stringify([
        { queryAll: '#some-id-1' },
        { queryAll: '#some-id-2', trackAs: null },
        { queryAll: '#some-id-3', trackAs: {} },
        { trackAs: trackElement({ id: 'element-id-1' }) },
        { queryAll: null, trackAs: trackElement({ id: 'element-id-2' }) },
        { queryAll: '', trackAs: trackElement({ id: 'element-id-3' }) },
      ])
    );

    expect(processChildrenTrackingElement(div)).toHaveLength(0);
  });

  it('should skip queries with failing querySelector expressions', () => {
    const div = document.createElement('div');
    div.setAttribute(
      TrackingAttribute.trackChildren,
      JSON.stringify([
        { queryAll: '#button-id-1', trackAs: trackButton({ id: 'button-id', text: 'button' }) },
        { queryAll: '[class="button"]', trackAs: trackButton({ id: 'button-id', text: 'button' }) },
      ])
    );

    expect(processChildrenTrackingElement(div)).toHaveLength(0);
  });

  it('should match the first query', () => {
    const div = document.createElement('div');
    const childButton = document.createElement('button');
    childButton.setAttribute('id', 'button-id-1');
    div.appendChild(childButton);
    document.body.appendChild(div);

    div.setAttribute(
      TrackingAttribute.trackChildren,
      JSON.stringify([
        { queryAll: '#button-id-1', trackAs: trackButton({ id: 'button-id', text: 'button' }) },
        { queryAll: '[class="button"]', trackAs: trackButton({ id: 'button-id', text: 'button' }) },
      ])
    );

    const result = processChildrenTrackingElement(div);

    const expectedButtonContext = makeButtonContext({ id: 'button-id', text: 'button' });

    expect(result).toHaveLength(1);
    expect(isTrackedElement(result[0])).toBe(true);
    expect(JSON.parse(result[0].getAttribute(TrackingAttribute.context) ?? '')).toStrictEqual(expectedButtonContext);
  });
});
