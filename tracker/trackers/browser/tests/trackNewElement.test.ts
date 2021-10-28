import {
  generateUUID,
  makeButtonContext,
  makeInputContext,
  makeSectionContext,
  makeSectionVisibleEvent,
} from '@objectiv/tracker-core';
import { BrowserTracker, getTracker, makeTracker, TaggingAttribute } from '../src';
import { trackNewElement } from '../src/observer/trackNewElement';
import { makeTaggedElement } from './mocks/makeTaggedElement';

describe('trackNewElement', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: generateUUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  it('should skip the Element if it is not a Tracked Element', async () => {
    const div = document.createElement('div');
    jest.spyOn(div, 'addEventListener');

    trackNewElement(div, getTracker());

    expect(div.addEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should skip the Element if it is already Tracked', async () => {
    const buttonContext = makeButtonContext({ id: 'test', text: 'test' });
    const trackedButton = makeTaggedElement('button-id-1', JSON.stringify(buttonContext), 'button');
    trackedButton.setAttribute(TaggingAttribute.tracked, 'true');
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not attach click event listener', async () => {
    const buttonContext = makeButtonContext({ id: 'test', text: 'test' });
    const trackedButton = makeTaggedElement('button-id-1', JSON.stringify(buttonContext), 'button');
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TaggingAttribute.trackClicks, 'false');
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should track visibility: visible event', async () => {
    const sectionContext = makeSectionContext({ id: 'test' });
    const trackedDiv = makeTaggedElement('div-id-1', 'test', 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');
    jest.spyOn(trackedDiv, 'addEventListener');

    trackNewElement(trackedDiv, getTracker());

    expect(trackedDiv.addEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      makeSectionVisibleEvent({ location_stack: [sectionContext] })
    );
  });

  it('should attach click event listener - passive', async () => {
    const buttonContext = makeButtonContext({ id: 'test', text: 'test' });
    const trackedButton = makeTaggedElement('button-id-1', JSON.stringify(buttonContext), 'button');
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TaggingAttribute.trackClicks, 'true');
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).toHaveBeenCalledTimes(1);
    expect(trackedButton.addEventListener).toHaveBeenNthCalledWith(1, 'click', expect.any(Function), { passive: true });
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should attach click event listener - capture', async () => {
    const buttonContext = makeButtonContext({ id: 'test', text: 'test' });
    const trackedButton = makeTaggedElement('button-id-1', JSON.stringify(buttonContext), 'button');
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TaggingAttribute.trackClicks, JSON.stringify({ waitUntilTracked: true }));
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).toHaveBeenCalledTimes(1);
    expect(trackedButton.addEventListener).toHaveBeenNthCalledWith(1, 'click', expect.any(Function), true);
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should attach click event listener - capture with custom options', async () => {
    const buttonContext = makeButtonContext({ id: 'test', text: 'test' });
    const trackedButton = makeTaggedElement('button-id-1', JSON.stringify(buttonContext), 'button');
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TaggingAttribute.trackClicks, JSON.stringify({ waitUntilTracked: { timeoutMs: 5000 } }));
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).toHaveBeenCalledTimes(1);
    expect(trackedButton.addEventListener).toHaveBeenNthCalledWith(1, 'click', expect.any(Function), true);
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not attach click event listener and console.error', async () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const buttonContext = makeButtonContext({ id: 'test', text: 'test' });
    const trackedButton = makeTaggedElement('button-id-1', JSON.stringify(buttonContext), 'button');
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TaggingAttribute.trackClicks, JSON.stringify({ waitUntilTracked: false }));
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledTimes(1);
  });

  it('should attach blur event listener', async () => {
    const inputContext = makeInputContext({ id: 'test' });
    const trackedInput = makeTaggedElement('input-id-1', JSON.stringify(inputContext), 'input');
    trackedInput.setAttribute(TaggingAttribute.trackBlurs, 'true');
    jest.spyOn(trackedInput, 'addEventListener');

    trackNewElement(trackedInput, getTracker());

    expect(trackedInput.addEventListener).toHaveBeenCalledTimes(1);
    expect(trackedInput.addEventListener).toHaveBeenNthCalledWith(1, 'blur', expect.any(Function), { passive: true });
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should console error', async () => {
    jest.resetAllMocks();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const inputContext = makeInputContext({ id: 'test' });
    const trackedInput = makeTaggedElement('input-id-1', JSON.stringify(inputContext), 'input');
    trackedInput.setAttribute(TaggingAttribute.trackBlurs, 'true');
    jest.spyOn(trackedInput, 'addEventListener').mockImplementation(() => {
      throw new Error('nope');
    });

    trackNewElement(trackedInput, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledTimes(1);
  });
});
