/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import {
  GlobalContextName,
  LocationContextName,
  makeContentContext,
  makeInputContext,
  makeInputValueContext,
  Tracker,
} from '@objectiv/tracker-core';
import { mergeEventTrackerHookAndCallbackParameters } from '../src';

describe('mergeEventTrackerHookAndCallbackParameters', () => {
  const tracker = new Tracker({ applicationId: 'app-id' });

  it('should use the tracker instance given as parameter to the hook', () => {
    const hookParamTracker = new Tracker({ applicationId: 'hook-param-tracker' });
    expect(mergeEventTrackerHookAndCallbackParameters({ tracker: hookParamTracker }, {})).toEqual({
      tracker: hookParamTracker,
      locationStack: [],
      globalContexts: [],
      options: undefined,
    });
  });

  it('should use the tracker instance given as parameter to the callback, cb has priority over hook', () => {
    const hookParamTracker = new Tracker({ applicationId: 'hook-param-tracker' });
    const cbParamTracker = new Tracker({ applicationId: 'cb-param-tracker' });
    expect(
      mergeEventTrackerHookAndCallbackParameters({ tracker: hookParamTracker }, { tracker: cbParamTracker })
    ).toEqual({
      tracker: cbParamTracker,
      locationStack: [],
      globalContexts: [],
      options: undefined,
    });
  });

  it('should use the hook options', () => {
    expect(mergeEventTrackerHookAndCallbackParameters({ tracker, options: { flushQueue: true } }, {})).toEqual({
      tracker: tracker,
      locationStack: [],
      globalContexts: [],
      options: {
        flushQueue: true,
      },
    });
  });

  it('should use the cb options', () => {
    expect(mergeEventTrackerHookAndCallbackParameters({ tracker }, { options: { flushQueue: true } })).toEqual({
      tracker: tracker,
      locationStack: [],
      globalContexts: [],
      options: {
        flushQueue: true,
      },
    });
  });

  it('should merge the cb options into the hook options', () => {
    expect(
      mergeEventTrackerHookAndCallbackParameters(
        { tracker, options: { flushQueue: true } },
        { options: { waitForQueue: true } }
      )
    ).toEqual({
      tracker: tracker,
      locationStack: [],
      globalContexts: [],
      options: {
        flushQueue: true,
        waitForQueue: true,
      },
    });
  });

  it('should merge the cb options into the hook options, cb overrides hook options with the same name', () => {
    expect(
      mergeEventTrackerHookAndCallbackParameters(
        { tracker, options: { waitForQueue: true } },
        { options: { waitForQueue: { timeoutMs: 100 } } }
      )
    ).toEqual({
      tracker: tracker,
      locationStack: [],
      globalContexts: [],
      options: {
        waitForQueue: {
          timeoutMs: 100,
        },
      },
    });
  });

  it('should merge the hook location stack and global contexts into the context one', () => {
    expect(
      mergeEventTrackerHookAndCallbackParameters(
        {
          tracker,
          locationStack: [makeInputContext({ id: 'test' })],
          globalContexts: [makeInputValueContext({ id: 'test', value: '1' })],
        },
        {}
      )
    ).toEqual({
      tracker,
      locationStack: [expect.objectContaining({ _type: LocationContextName.InputContext, id: 'test' })],
      globalContexts: [expect.objectContaining({ _type: GlobalContextName.InputValueContext, id: 'test', value: '1' })],
      options: undefined,
    });
  });

  it('should merge the callback location stack and global contexts into the context one', () => {
    expect(
      mergeEventTrackerHookAndCallbackParameters(
        { tracker },
        {
          locationStack: [makeInputContext({ id: 'test' })],
          globalContexts: [makeInputValueContext({ id: 'test', value: '1' })],
        }
      )
    ).toEqual({
      tracker,
      locationStack: [expect.objectContaining({ _type: LocationContextName.InputContext, id: 'test' })],
      globalContexts: [expect.objectContaining({ _type: GlobalContextName.InputValueContext, id: 'test', value: '1' })],
      options: undefined,
    });
  });

  it('should merge both the hook and the callback location stacks and global contexts into the context one', () => {
    expect(
      mergeEventTrackerHookAndCallbackParameters(
        {
          tracker,
          locationStack: [makeContentContext({ id: 'hook-location' })],
          globalContexts: [makeInputValueContext({ id: 'hook-global', value: '1' })],
        },
        {
          locationStack: [makeInputContext({ id: 'cb-location' })],
          globalContexts: [makeInputValueContext({ id: 'cb-global', value: '2' })],
        }
      )
    ).toEqual({
      tracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'hook-location' }),
        expect.objectContaining({ _type: LocationContextName.InputContext, id: 'cb-location' }),
      ],
      globalContexts: [
        expect.objectContaining({ _type: GlobalContextName.InputValueContext, id: 'hook-global', value: '1' }),
        expect.objectContaining({ _type: GlobalContextName.InputValueContext, id: 'cb-global', value: '2' }),
      ],
      options: undefined,
    });
  });
});
