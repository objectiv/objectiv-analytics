/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { localStorageMock, MockConsoleImplementation } from '@objectiv/testing-tools';
import { TrackerEvent } from '@objectiv/tracker-core';
import { LocalStorageQueueStore } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('LocalStorageQueueStore', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  const TrackerEvent1 = new TrackerEvent({ id: 'a', _type: 'a', time: Date.now() });
  const TrackerEvent2 = new TrackerEvent({ id: 'b', _type: 'b', time: Date.now() });
  const TrackerEvent3 = new TrackerEvent({ id: 'c', _type: 'c', time: Date.now() });

  describe('Isolation', () => {
    afterEach(() => {
      localStorage.clear();
    });

    it('should read all Events', async () => {
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'app-id' });
      await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
      expect(trackerQueueStore.length).toBe(3);

      const events = await trackerQueueStore.read();

      expect(events.map((event) => event.id)).toStrictEqual(['a', 'b', 'c']);
    });

    it('should read two Events', async () => {
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'app-id' });
      await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
      expect(trackerQueueStore.length).toBe(3);

      const events = await trackerQueueStore.read(2);

      expect(events.map((event) => event.id)).toStrictEqual(['a', 'b']);
    });

    it('should allow filtering when reading Events', async () => {
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'app-id' });
      await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
      expect(trackerQueueStore.length).toBe(3);

      const events = await trackerQueueStore.read(Infinity, (event) => event.id !== 'a');

      expect(events.map((event) => event.id)).toStrictEqual(['b', 'c']);
    });

    it('should delete Events', async () => {
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'app-id' });
      await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
      expect(trackerQueueStore.length).toBe(3);

      await trackerQueueStore.delete(['b']);

      expect(trackerQueueStore.length).toBe(2);
      expect((await trackerQueueStore.read()).map((event) => event.id)).toStrictEqual(['a', 'c']);

      await trackerQueueStore.delete(['a', 'c']);

      expect(trackerQueueStore.length).toBe(0);
      expect(await trackerQueueStore.read()).toStrictEqual([]);
    });

    it('should delete all Events', async () => {
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'app-id' });
      await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
      expect(trackerQueueStore.length).toBe(3);

      await trackerQueueStore.clear();

      expect(trackerQueueStore.length).toBe(0);
      expect(await trackerQueueStore.read()).toStrictEqual([]);
    });
  });

  describe('Persistence', () => {
    it('should write three events in the store', async () => {
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'app-id' });
      await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
      expect(trackerQueueStore.length).toBe(3);
      const events = await trackerQueueStore.read();
      expect(events.map((event) => event.id)).toStrictEqual(['a', 'b', 'c']);
    });

    it('should be able to access the events written in the previous test', async () => {
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'app-id' });
      expect(trackerQueueStore.length).toBe(3);
      const events = await trackerQueueStore.read();
      expect(events.map((event) => event.id)).toStrictEqual(['a', 'b', 'c']);
    });
  });

  describe('Error handling', () => {
    const originalSetItemMock = localStorageMock.setItem;

    afterEach(() => {
      localStorage.clear();
      jest.clearAllMocks();
      localStorageMock.setItem = originalSetItemMock;
    });

    it('should return empty array if the store is corrupted', async () => {
      const trackerId = 'broken';
      const corruptedValue = '[ooops';
      const localStorageKey = `objectiv-events-queue-${trackerId}`;
      localStorage.setItem(localStorageKey, corruptedValue);
      expect(localStorage.getItem(localStorageKey)).toBe(corruptedValue);
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'broken' });
      expect(trackerQueueStore.length).toBe(0);
      const events = await trackerQueueStore.read();
      expect(events).toStrictEqual([]);
    });

    it('should console.error if the store is corrupted', async () => {
      const trackerId = 'broken';
      const corruptedValue = '[ooops';
      const localStorageKey = `objectiv-events-queue-${trackerId}`;
      localStorage.setItem(localStorageKey, corruptedValue);
      expect(localStorage.getItem(localStorageKey)).toBe(corruptedValue);
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'broken' });
      expect(trackerQueueStore.length).toBe(0);
      const events = await trackerQueueStore.read();
      expect(events).toStrictEqual([]);
      // Once for the length getter, once for the read method
      expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
      expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:LocalStorageQueueStore｣ Failed to parse Events from localStorage: SyntaxError: Unexpected token o in JSON at position 1',
        'font-weight: bold'
      );
      expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
        2,
        '%c｢objectiv:LocalStorageQueueStore｣ Failed to parse Events from localStorage: SyntaxError: Unexpected token o in JSON at position 1',
        'font-weight: bold'
      );
    });

    it('should not crash if writing to local storage fails', async () => {
      localStorageMock.setItem = jest.fn().mockImplementation(() => {
        throw Error('nope');
      });
      Object.defineProperty(window, 'localStorage', { value: localStorageMock });
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'app-id' });
      expect(trackerQueueStore.length).toBe(0);
      await trackerQueueStore.write(TrackerEvent1);
    });

    it('should console.error if the given Events are invalid', async () => {
      localStorageMock.setItem = jest.fn().mockImplementation(() => {
        throw Error('nope');
      });
      Object.defineProperty(window, 'localStorage', { value: localStorageMock });
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'app-id' });
      expect(trackerQueueStore.length).toBe(0);
      await trackerQueueStore.write(TrackerEvent1);
      expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
        1,
        '%c｢objectiv:LocalStorageQueueStore｣ Failed to write Events to localStorage: Error: nope',
        'font-weight: bold'
      );
    });
  });

  describe('Without developer tools', () => {
    let objectivGlobal = globalThis.objectiv;

    beforeEach(() => {
      localStorage.clear();
      jest.clearAllMocks();
      globalThis.objectiv.devTools = undefined;
    });

    afterEach(() => {
      globalThis.objectiv = objectivGlobal;
    });

    it('should not console.error if the store is corrupted', async () => {
      const trackerId = 'broken';
      const corruptedValue = '[ooops';
      const localStorageKey = `objectiv-events-queue-${trackerId}`;
      localStorage.setItem(localStorageKey, corruptedValue);
      expect(localStorage.getItem(localStorageKey)).toBe(corruptedValue);
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'broken' });
      expect(trackerQueueStore.length).toBe(0);
      const events = await trackerQueueStore.read();
      expect(events).toStrictEqual([]);
      // Once for the length getter, once for the read method
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should not console.error if the given Events are invalid', async () => {
      localStorageMock.setItem = jest.fn().mockImplementation(() => {
        throw Error('nope');
      });
      Object.defineProperty(window, 'localStorage', { value: localStorageMock });
      const trackerQueueStore = new LocalStorageQueueStore({ trackerId: 'app-id' });
      expect(trackerQueueStore.length).toBe(0);
      await trackerQueueStore.write(TrackerEvent1);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
