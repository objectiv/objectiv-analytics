import { StructError } from 'superstruct';
import { tagChild, tagChildren, tagElement, TaggingAttribute } from '../src';

describe('tagChild and tagChildren', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should return an empty object when error occurs', () => {
    // @ts-ignore
    expect(tagChild()).toBeUndefined();
    // @ts-ignore
    expect(tagChildren()).toBeUndefined();
    // @ts-ignore
    expect(tagChild([])).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ tagAs: tagElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ queryAll: null, tagAs: tagElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ queryAll: undefined, tagAs: tagElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ queryAll: 0, tagAs: tagElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ queryAll: false, tagAs: tagElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ queryAll: true, tagAs: tagElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ queryAll: {}, tagAs: tagElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ queryAll: Infinity, tagAs: tagElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ queryAll: -Infinity, tagAs: tagElement({ id: 'test' }) })).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ query: -Infinity, tagAs: undefined })).toBeUndefined();
    // @ts-ignore
    expect(tagChild({ queryAll: -Infinity, tagAs: undefined })).toBeUndefined();
  });

  it('should call `onError` callback when an error occurs', () => {
    const errorCallback = jest.fn();

    // @ts-ignore
    tagChild({ query: {} }, errorCallback);

    expect(errorCallback).toHaveBeenCalledTimes(1);
    expect(errorCallback.mock.calls[0][0]).toBeInstanceOf(StructError);
  });

  it('should call `console.error` when an error occurs and `onError` has not been provided', () => {
    jest.spyOn(console, 'error');

    // @ts-ignore
    tagChild({ queryAll: {} });

    expect(console.error).toHaveBeenCalledTimes(1);
  });

  it('should return query and tagAs attributes', () => {
    jest.spyOn(console, 'error');
    const parameters = { queryAll: '#two', tagAs: tagElement({ id: 'element-two' }) };

    const attributes1 = tagChild(parameters);
    const attributes2 = tagChildren([parameters]);

    expect(console.error).not.toHaveBeenCalled();
    expect(attributes1).toStrictEqual({
      [TaggingAttribute.tagChildren]: JSON.stringify([parameters]),
    });
    expect(attributes2).toStrictEqual({
      [TaggingAttribute.tagChildren]: JSON.stringify([parameters]),
    });
  });
});
