/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID, GlobalContextName, LocationContextName, makeInputChangeEvent } from '@objectiv/tracker-core';
import { BrowserTracker, getTracker, getTrackerRepository, makeTracker } from '../src/';
import { makeBlurEventHandler } from '../src/mutationObserver/makeBlurEventHandler';
import { makeTaggedElement } from './mocks/makeTaggedElement';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('makeBlurEventHandler', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: generateGUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  afterEach(() => {
    getTrackerRepository().trackersMap = new Map();
    getTrackerRepository().defaultTracker = undefined;
    jest.resetAllMocks();
  });

  it('should track Input Change when invoked from a valid target (HTMLInputElement)', () => {
    const trackedInput = makeTaggedElement('input', null, 'input');
    const blurEventListener = makeBlurEventHandler(trackedInput);

    trackedInput.addEventListener('blur', blurEventListener);
    trackedInput.dispatchEvent(new FocusEvent('blur'));

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        global_contexts: [],
        location_stack: [],
      })
    );
  });

  it('should include InputValueContext when invoked with the trackValue option (HTMLInputElement)', () => {
    const trackedInput = makeTaggedElement('input', 'test-input', 'input', false, true);
    trackedInput.setAttribute('value', 'test value');
    const blurEventListener = makeBlurEventHandler(trackedInput, undefined, { trackValue: true }, 'test-input');

    trackedInput.addEventListener('blur', blurEventListener);
    trackedInput.dispatchEvent(new FocusEvent('blur'));

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        global_contexts: expect.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.InputValueContext,
            id: 'test-input',
            value: 'test value',
          }),
        ]),
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'test-input',
          }),
        ]),
      })
    );
  });

  it('should include InputValueContext when invoked with the trackValue option (HTMLSelectElement)', () => {
    const trackedInput = makeTaggedElement('input', 'test-input', 'select', false, true);
    const inputOption = document.createElement('option');
    inputOption.setAttribute('value', 'test value');
    trackedInput.setAttribute('selectedIndex', '0');
    trackedInput.append(inputOption);
    const blurEventListener = makeBlurEventHandler(trackedInput, undefined, { trackValue: true }, 'test-input');

    trackedInput.addEventListener('blur', blurEventListener);
    trackedInput.dispatchEvent(new FocusEvent('blur'));

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        global_contexts: expect.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.InputValueContext,
            id: 'test-input',
            value: 'test value',
          }),
        ]),
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'test-input',
          }),
        ]),
      })
    );
  });

  it('should not track Input Change when invoked from a bubbling target', () => {
    const trackedInput = makeTaggedElement('input1', null, 'input');
    const unrelatedInput = makeTaggedElement('input2', null, 'input');
    const blurEventListener = makeBlurEventHandler(trackedInput);

    trackedInput.addEventListener('blur', blurEventListener);
    unrelatedInput.dispatchEvent(new FocusEvent('blur'));

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not track Input Change when current target is not a click-tracking tagged element', () => {
    const span = document.createElement('span');
    const trackedInput = makeTaggedElement('input', 'input', 'input', false, false);
    trackedInput.appendChild(span);
    const inputEventListener = jest.fn(makeBlurEventHandler(trackedInput, getTracker()));

    trackedInput.addEventListener('blur', inputEventListener);
    span.dispatchEvent(new MouseEvent('blur', { bubbles: true }));

    expect(inputEventListener).toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should track Input Change when invoked from a non-tagged child', () => {
    const span = document.createElement('span');
    const trackedInput = makeTaggedElement('input', 'input', 'input', false, true);
    trackedInput.appendChild(span);
    const inputEventListener = jest.fn(makeBlurEventHandler(trackedInput, getTracker()));

    trackedInput.addEventListener('blur', inputEventListener);
    span.dispatchEvent(new MouseEvent('blur', { bubbles: true }));

    expect(inputEventListener).toHaveBeenCalled();
    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(
        makeInputChangeEvent({
          location_stack: [expect.objectContaining({ _type: LocationContextName.InputContext, id: 'input' })],
        })
      )
    );
  });
});
