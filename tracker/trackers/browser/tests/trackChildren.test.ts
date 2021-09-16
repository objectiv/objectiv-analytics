import { StructError } from 'superstruct';
import { trackChild, trackChildren, trackElement, TrackingAttribute } from '../src';

describe('trackChild and trackChildren', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should return an empty object when error occurs', () => {
    // @ts-ignore
    expect(trackChild()).toBeUndefined();
    // @ts-ignore
    expect(trackChildren()).toBeUndefined();
    // @ts-ignore
    expect(trackChild([])).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ trackAs: trackElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ queryAll: null, trackAs: trackElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ queryAll: undefined, trackAs: trackElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ queryAll: 0, trackAs: trackElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ queryAll: false, trackAs: trackElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ queryAll: true, trackAs: trackElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ queryAll: {}, trackAs: trackElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ queryAll: Infinity, trackAs: trackElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ queryAll: -Infinity, trackAs: trackElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ query: -Infinity, trackAs: undefined })).toBeUndefined();
    // @ts-ignore
    expect(trackChild({ queryAll: -Infinity, trackAs: undefined })).toBeUndefined();
  });

  it('should call `onError` callback when an error occurs', () => {
    const errorCallback = jest.fn();

    // @ts-ignore
    trackChild({ query: {} }, errorCallback);

    expect(errorCallback).toHaveBeenCalledTimes(1);
    expect(errorCallback.mock.calls[0][0]).toBeInstanceOf(StructError);
  });

  it('should call `console.error` when an error occurs and `onError` has not been provided', () => {
    jest.spyOn(console, 'error');

    // @ts-ignore
    trackChild({ queryAll: {} });

    expect(console.error).toHaveBeenCalledTimes(1);
  });

  it('should return query and trackAs attributes', () => {
    jest.spyOn(console, 'error');
    const parameters = { queryAll: '#two', trackAs: trackElement({ id: 'element-two' }) };

    // @ts-ignore
    const attributes = trackChild(parameters);

    expect(console.error).not.toHaveBeenCalled();
    expect(attributes).toStrictEqual({
      [TrackingAttribute.trackChildren]: JSON.stringify([parameters]),
    });
  });
});
