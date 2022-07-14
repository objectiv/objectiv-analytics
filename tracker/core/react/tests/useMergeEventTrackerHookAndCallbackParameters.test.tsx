/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import {
  GlobalContextName,
  LocationContextName,
  makeContentContext,
  makeInputContext,
  makeInputValueContext,
  makeRootLocationContext,
  Tracker,
} from '@objectiv/tracker-core';
import { renderHook } from '@testing-library/react-hooks';
import React from 'react';
import { ContentContextWrapper, TrackingContextProvider, useMergeEventTrackerHookAndCallbackParameters } from '../src';

describe('useMergeEventTrackerHookAndCallbackParameters', () => {
  const tracker = new Tracker({ applicationId: 'app-id' });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <TrackingContextProvider tracker={tracker} locationStack={[makeRootLocationContext({ id: 'root' })]}>
      <ContentContextWrapper id={'wrapper'}>{children}</ContentContextWrapper>
    </TrackingContextProvider>
  );

  it('should use the tracker instance and location stack coming from TrackingContextProvider', () => {
    const { result } = renderHook(() => useMergeEventTrackerHookAndCallbackParameters({}, {}), { wrapper });
    expect(result.current).toEqual({
      tracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'wrapper' }),
      ],
      globalContexts: [],
      options: undefined,
    });
  });

  it('should use the tracker instance given as parameter to the hook', () => {
    const hookParamTracker = new Tracker({ applicationId: 'hook-param-tracker' });
    const { result } = renderHook(
      () => useMergeEventTrackerHookAndCallbackParameters({ tracker: hookParamTracker }, {}),
      { wrapper }
    );
    expect(result.current).toEqual({
      tracker: hookParamTracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'wrapper' }),
      ],
      globalContexts: [],
      options: undefined,
    });
  });

  it('should use the tracker instance given as parameter to the callback, cb has priority over hook', () => {
    const hookParamTracker = new Tracker({ applicationId: 'hook-param-tracker' });
    const cbParamTracker = new Tracker({ applicationId: 'cb-param-tracker' });
    const { result } = renderHook(
      () => useMergeEventTrackerHookAndCallbackParameters({ tracker: hookParamTracker }, { tracker: cbParamTracker }),
      { wrapper }
    );
    expect(result.current).toEqual({
      tracker: cbParamTracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'wrapper' }),
      ],
      globalContexts: [],
      options: undefined,
    });
  });

  it('should use the hook options', () => {
    const { result } = renderHook(
      () => useMergeEventTrackerHookAndCallbackParameters({ options: { flushQueue: true } }, {}),
      { wrapper }
    );
    expect(result.current).toEqual({
      tracker: tracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'wrapper' }),
      ],
      globalContexts: [],
      options: {
        flushQueue: true,
      },
    });
  });

  it('should use the cb options', () => {
    const { result } = renderHook(
      () => useMergeEventTrackerHookAndCallbackParameters({}, { options: { flushQueue: true } }),
      { wrapper }
    );
    expect(result.current).toEqual({
      tracker: tracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'wrapper' }),
      ],
      globalContexts: [],
      options: {
        flushQueue: true,
      },
    });
  });

  it('should merge the cb options into the hook options', () => {
    const { result } = renderHook(
      () =>
        useMergeEventTrackerHookAndCallbackParameters(
          { options: { flushQueue: true } },
          { options: { waitForQueue: true } }
        ),
      { wrapper }
    );
    expect(result.current).toEqual({
      tracker: tracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'wrapper' }),
      ],
      globalContexts: [],
      options: {
        flushQueue: true,
        waitForQueue: true,
      },
    });
  });

  it('should merge the cb options into the hook options, cb overrides hook options with the same name', () => {
    const { result } = renderHook(
      () =>
        useMergeEventTrackerHookAndCallbackParameters(
          { options: { waitForQueue: true } },
          { options: { waitForQueue: { timeoutMs: 100 } } }
        ),
      { wrapper }
    );
    expect(result.current).toEqual({
      tracker: tracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'wrapper' }),
      ],
      globalContexts: [],
      options: {
        waitForQueue: {
          timeoutMs: 100,
        },
      },
    });
  });

  it('should merge the hook location stack and global contexts into the context one', () => {
    const { result } = renderHook(
      () =>
        useMergeEventTrackerHookAndCallbackParameters(
          {
            locationStack: [makeInputContext({ id: 'test' })],
            globalContexts: [makeInputValueContext({ id: 'test', value: '1' })],
          },
          {}
        ),
      { wrapper }
    );
    expect(result.current).toEqual({
      tracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'wrapper' }),
        expect.objectContaining({ _type: LocationContextName.InputContext, id: 'test' }),
      ],
      globalContexts: [expect.objectContaining({ _type: GlobalContextName.InputValueContext, id: 'test', value: '1' })],
      options: undefined,
    });
  });

  it('should merge the callback location stack and global contexts into the context one', () => {
    const { result } = renderHook(
      () =>
        useMergeEventTrackerHookAndCallbackParameters(
          {},
          {
            locationStack: [makeInputContext({ id: 'test' })],
            globalContexts: [makeInputValueContext({ id: 'test', value: '1' })],
          }
        ),
      { wrapper }
    );
    expect(result.current).toEqual({
      tracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'wrapper' }),
        expect.objectContaining({ _type: LocationContextName.InputContext, id: 'test' }),
      ],
      globalContexts: [expect.objectContaining({ _type: GlobalContextName.InputValueContext, id: 'test', value: '1' })],
      options: undefined,
    });
  });

  it('should merge both the hook and the callback location stacks and global contexts into the context one', () => {
    const { result } = renderHook(
      () =>
        useMergeEventTrackerHookAndCallbackParameters(
          {
            locationStack: [makeContentContext({ id: 'hook-location' })],
            globalContexts: [makeInputValueContext({ id: 'hook-global', value: '1' })],
          },
          {
            locationStack: [makeInputContext({ id: 'cb-location' })],
            globalContexts: [makeInputValueContext({ id: 'cb-global', value: '2' })],
          }
        ),
      { wrapper }
    );
    expect(result.current).toEqual({
      tracker,
      locationStack: [
        expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
        expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'wrapper' }),
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
