/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  BrowserTracker,
  getOrMakeTracker,
  getTracker,
  makeTracker,
  setDefaultTracker,
  TrackerRepository,
} from '../src/';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('globals', () => {
  afterEach(() => {
    TrackerRepository.trackersMap.clear();
    TrackerRepository.defaultTracker = undefined;
    jest.resetAllMocks();
  });
  beforeEach(() => {
    expect(TrackerRepository.trackersMap.size).toBe(0);
  });

  it('should create a new Browser Tracker in window.object.tracker and start auto tracking', () => {
    makeTracker({ applicationId: 'app-id', endpoint: 'localhost' });
    expect(TrackerRepository.trackersMap.size).toBe(1);
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
  });

  it('should create three new Browser Trackers and getTracker should return the first one', () => {
    makeTracker({ applicationId: 'app-id-1', endpoint: 'localhost' });
    makeTracker({ applicationId: 'app-id-2', endpoint: 'localhost' });
    makeTracker({ applicationId: 'app-id-3', endpoint: 'localhost' });
    expect(TrackerRepository.trackersMap.size).toBe(3);
    expect(getTracker().applicationId).toBe('app-id-1');
    expect(getTracker('app-id-1').applicationId).toBe('app-id-1');
    expect(getTracker('app-id-2').applicationId).toBe('app-id-2');
    expect(getTracker('app-id-3').applicationId).toBe('app-id-3');
  });

  it('should allow changing default Browser Tracker', async () => {
    makeTracker({ applicationId: 'app-id-1', endpoint: 'localhost' });
    makeTracker({ applicationId: 'app-id-2', endpoint: 'localhost' });
    makeTracker({ applicationId: 'app-id-3', endpoint: 'localhost' });
    expect(TrackerRepository.trackersMap.size).toBe(3);
    expect(getTracker().applicationId).toBe('app-id-1');
    await setDefaultTracker('app-id-2');
    expect(getTracker().applicationId).toBe('app-id-2');
    await setDefaultTracker('app-id-3');
    expect(getTracker().applicationId).toBe('app-id-3');
    await setDefaultTracker('app-id-1');
    expect(getTracker().applicationId).toBe('app-id-1');
  });

  it('should allow changing default Browser Tracker and specify custom options', async () => {
    makeTracker({ applicationId: 'app-id-1', endpoint: 'localhost' });
    makeTracker({ applicationId: 'app-id-2', endpoint: 'localhost' });
    expect(TrackerRepository.trackersMap.size).toBe(2);
    expect(getTracker().applicationId).toBe('app-id-1');
    await setDefaultTracker({ trackerId: 'app-id-2' });
    expect(getTracker().applicationId).toBe('app-id-2');
    await setDefaultTracker({ trackerId: 'app-id-1' });
    expect(getTracker().applicationId).toBe('app-id-1');
    await setDefaultTracker({ trackerId: 'app-id-2', waitForQueue: {} });
    expect(getTracker().applicationId).toBe('app-id-2');
    await setDefaultTracker({ trackerId: 'app-id-1', waitForQueue: false });
    expect(getTracker().applicationId).toBe('app-id-1');
    await setDefaultTracker({ trackerId: 'app-id-2', flushQueue: true });
    expect(getTracker().applicationId).toBe('app-id-2');
    await setDefaultTracker({ trackerId: 'app-id-1', flushQueue: false });
    expect(getTracker().applicationId).toBe('app-id-1');
    await setDefaultTracker({ trackerId: 'app-id-1', flushQueue: 'onTimeout' });
    expect(getTracker().applicationId).toBe('app-id-1');
  });

  it('should allow creating multiple Browser Trackers for the same application', () => {
    makeTracker({ applicationId: 'app-id', trackerId: 'tracker-1', endpoint: 'localhost' });
    makeTracker({ applicationId: 'app-id', trackerId: 'tracker-2', endpoint: 'localhost' });
    makeTracker({ applicationId: 'app-id', trackerId: 'tracker-3', endpoint: 'localhost' });
    expect(TrackerRepository.trackersMap.size).toBe(3);
    expect(() => getTracker('app-id-1')).toThrow('No Tracker found. Please create one via `makeTracker`.');
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ Tracker `app-id-1` not found.'
    );
    expect(getTracker('tracker-1').applicationId).toBe('app-id');
    expect(getTracker('tracker-2').applicationId).toBe('app-id');
    expect(getTracker('tracker-3').applicationId).toBe('app-id');
  });

  it('should not allow overwriting an existing Browser Trackers instance', () => {
    makeTracker({ applicationId: 'app-id', trackerId: 'tracker-1', endpoint: 'localhost' });
    makeTracker({ applicationId: 'tracker-1', endpoint: 'localhost' });
    expect(TrackerRepository.trackersMap.size).toBe(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ Tracker `tracker-1` already exists.'
    );
    makeTracker({ applicationId: 'app-id', trackerId: 'tracker-1', endpoint: 'localhost' });
    expect(TrackerRepository.trackersMap.size).toBe(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      2,
      '｢objectiv:TrackerRepository｣ Tracker `tracker-1` already exists.'
    );
  });

  it('should create a new Browser Tracker ', () => {
    expect(TrackerRepository.trackersMap.size).toBe(0);
    expect(getOrMakeTracker({ applicationId: 'app-id', trackerId: 'tracker1', endpoint: 'localhost' })).toBeInstanceOf(
      BrowserTracker
    );
    expect(TrackerRepository.trackersMap.size).toBe(1);
  });

  it('should return the existing Browser Tracker', () => {
    expect(TrackerRepository.trackersMap.size).toBe(0);
    const trackerConfig = { applicationId: 'app-id', endpoint: 'localhost' };
    makeTracker(trackerConfig);
    expect(TrackerRepository.trackersMap.size).toBe(1);
    expect(getOrMakeTracker(trackerConfig)).toBeInstanceOf(BrowserTracker);
    expect(TrackerRepository.trackersMap.size).toBe(1);
  });

  it('should TrackerConsole.error because a Browser Tracker exists with the same Tracker Id but has a different configuration', () => {
    const trackerConfig1 = { applicationId: 'app-id', endpoint: 'localhost' };
    const trackerConfig2 = { applicationId: 'app-id', endpoint: 'http://collector' };
    expect(TrackerRepository.trackersMap.size).toBe(0);
    makeTracker(trackerConfig1);
    expect(TrackerRepository.trackersMap.size).toBe(1);
    getOrMakeTracker(trackerConfig2);
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      "Tracker `app-id` exists but its configuration doesn't match the given one. This means getOrMakeTracker has been called twice with different configs."
    );
  });

  describe('Without developer tools', () => {
    let objectivGlobal = globalThis.objectiv;

    beforeEach(() => {
      jest.clearAllMocks();
      globalThis.objectiv = undefined;
    });

    afterEach(() => {
      globalThis.objectiv = objectivGlobal;
    });

    it('should not TrackerConsole.error because a Browser Tracker exists with the same Tracker Id but has a different configuration', () => {
      const trackerConfig1 = { applicationId: 'app-id', endpoint: 'localhost' };
      const trackerConfig2 = { applicationId: 'app-id', endpoint: 'http://collector' };
      expect(TrackerRepository.trackersMap.size).toBe(0);
      makeTracker(trackerConfig1);
      expect(TrackerRepository.trackersMap.size).toBe(1);
      getOrMakeTracker(trackerConfig2);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
