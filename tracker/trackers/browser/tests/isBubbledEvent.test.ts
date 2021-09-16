import isBubbledEvent from '../src/observer/isBubbledEvent';
import makeTrackedElement from './mocks/makeTrackedElement';

describe('isBubbledEvent', () => {
  it('should return true', async () => {
    const trackedDiv1 = makeTrackedElement('div-id-1', 'context', 'div');
    const trackedDiv2 = makeTrackedElement('div-id-2', 'context', 'div');

    expect(isBubbledEvent(trackedDiv1, trackedDiv2)).toBe(true);
  });

  it('should return false', async () => {
    const trackedDiv1 = makeTrackedElement('div-id-1', 'context', 'div');
    const trackedDiv2 = makeTrackedElement('div-id-2', 'context', 'div');
    const regularDiv = document.createElement('div');

    expect(isBubbledEvent(trackedDiv1, trackedDiv1)).toBe(false);
    expect(isBubbledEvent(trackedDiv1, regularDiv)).toBe(false);
    expect(isBubbledEvent(trackedDiv2, trackedDiv2)).toBe(false);
    expect(isBubbledEvent(trackedDiv2, regularDiv)).toBe(false);
  });

  it('should console error', async () => {
    jest.spyOn(console, 'error');
    const trackedDiv2 = makeTrackedElement('div-id-2', 'context', 'div');

    // @ts-ignore
    expect(isBubbledEvent(null, trackedDiv2)).toBe(false);
    expect(console.error).toHaveBeenCalledTimes(1);
  });
});
