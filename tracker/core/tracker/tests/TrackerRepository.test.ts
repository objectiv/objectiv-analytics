/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { Tracker } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackerRepository', () => {
  beforeEach(() => {
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
    jest.resetAllMocks();
  });

  it('should console.error when attempting to get a Tracker from an empty TrackerRepository', () => {
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(0);
    expect(globalThis.objectiv.TrackerRepository.get()).toBeUndefined();
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith('｢objectiv:TrackerRepository｣ There are no Trackers.');
  });

  it('should console.error when attempting to set a default Tracker that does not exist', () => {
    new Tracker({ applicationId: 'app-id-1' });
    new Tracker({ applicationId: 'app-id-2' });
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(2);
    globalThis.objectiv.TrackerRepository.setDefault('app-id-3');
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ Tracker `app-id-3` not found.'
    );
  });

  it('should make only the first added new Tracker the default tracker', () => {
    new Tracker({ applicationId: 'app-id-1' });
    new Tracker({ applicationId: 'app-id-2' });
    new Tracker({ applicationId: 'app-id-3' });
    expect(globalThis.objectiv.TrackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
  });

  it('should not allow deleting the default Tracker when there are multiple trackers', () => {
    new Tracker({ applicationId: 'app-id-1' });
    new Tracker({ applicationId: 'app-id-2' });
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(2);
    expect(globalThis.objectiv.TrackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
    globalThis.objectiv.TrackerRepository.delete('app-id-1');
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ `app-id-1` is the default Tracker. Please set another as default before deleting it.'
    );
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(2);
    expect(globalThis.objectiv.TrackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
    globalThis.objectiv.TrackerRepository.setDefault('app-id-2');
    globalThis.objectiv.TrackerRepository.delete('app-id-1');
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(1);
    expect(globalThis.objectiv.TrackerRepository.defaultTracker?.applicationId).toBe('app-id-2');
  });

  it('should add a new Tracker in the trackersMap', () => {
    new Tracker({ applicationId: 'app-id' });
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(1);
    expect(globalThis.objectiv.TrackerRepository.get()).toBeInstanceOf(Tracker);
    expect(globalThis.objectiv.TrackerRepository.get()?.applicationId).toBe('app-id');
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
  });

  it('should delete an existing Tracker from the trackersMap', () => {
    new Tracker({ applicationId: 'app-id' });
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(1);
    expect(globalThis.objectiv.TrackerRepository.get()).toBeInstanceOf(Tracker);
    expect(globalThis.objectiv.TrackerRepository.get()?.applicationId).toBe('app-id');
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    globalThis.objectiv.TrackerRepository.delete('app-id');
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(0);
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
  });

  it('should create three new Trackers and get should return the first one', () => {
    new Tracker({ applicationId: 'app-id-1' });
    new Tracker({ applicationId: 'app-id-2' });
    new Tracker({ applicationId: 'app-id-3' });
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(3);
    expect(globalThis.objectiv.TrackerRepository.get()?.applicationId).toBe('app-id-1');
    expect(globalThis.objectiv.TrackerRepository.get('app-id-1')?.applicationId).toBe('app-id-1');
    expect(globalThis.objectiv.TrackerRepository.get('app-id-2')?.applicationId).toBe('app-id-2');
    expect(globalThis.objectiv.TrackerRepository.get('app-id-3')?.applicationId).toBe('app-id-3');
  });

  it('should allow creating multiple Trackers for the same application', () => {
    new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' });
    new Tracker({ applicationId: 'app-id', trackerId: 'tracker-2' });
    new Tracker({ applicationId: 'app-id', trackerId: 'tracker-3' });
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(3);
    expect(globalThis.objectiv.TrackerRepository.get('app-id-1')).toBeUndefined();
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ Tracker `app-id-1` not found.'
    );
    expect(globalThis.objectiv.TrackerRepository.get('tracker-1')?.applicationId).toBe('app-id');
    expect(globalThis.objectiv.TrackerRepository.get('tracker-2')?.applicationId).toBe('app-id');
    expect(globalThis.objectiv.TrackerRepository.get('tracker-3')?.applicationId).toBe('app-id');
  });

  it('should reuse an existing Tracker instance', () => {
    new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' });
    new Tracker({ applicationId: 'tracker-1' });
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(1);
    expect(MockConsoleImplementation.log).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ Tracker `tracker-1` already exists. Reusing existing instance.'
    );
    jest.resetAllMocks();
    new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' });
    expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(1);
    expect(MockConsoleImplementation.log).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ Tracker `tracker-1` already exists. Reusing existing instance.'
    );
  });

  it('should activate all inactive Tracker instances', () => {
    const tracker1 = new Tracker({ applicationId: 'app-id-1', active: false });
    tracker1.plugins.plugins = [];
    const tracker2 = new Tracker({ applicationId: 'app-id-2' });
    tracker2.plugins.plugins = [];
    const tracker3 = new Tracker({ applicationId: 'app-id-3', active: false });
    tracker3.plugins.plugins = [];
    jest.resetAllMocks();
    globalThis.objectiv.TrackerRepository.activateAll();
    expect(MockConsoleImplementation.log).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
      1,
      '%c｢objectiv:Tracker:app-id-1｣ New state: active',
      'font-weight: bold'
    );
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
      2,
      '%c｢objectiv:Tracker:app-id-3｣ New state: active',
      'font-weight: bold'
    );
  });

  it('should deactivate all active Tracker instances', () => {
    new Tracker({ applicationId: 'app-id-1' });
    new Tracker({ applicationId: 'app-id-2', active: false });
    new Tracker({ applicationId: 'app-id-3' });
    jest.resetAllMocks();
    globalThis.objectiv.TrackerRepository.deactivateAll();
    expect(MockConsoleImplementation.log).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
      1,
      '%c｢objectiv:Tracker:app-id-1｣ New state: inactive',
      'font-weight: bold'
    );
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
      2,
      '%c｢objectiv:Tracker:app-id-3｣ New state: inactive',
      'font-weight: bold'
    );
  });

  it('should call flushQueue for all active Tracker instances', () => {
    const tracker1 = new Tracker({ applicationId: 'app-id-1' });
    const tracker2 = new Tracker({ applicationId: 'app-id-2', active: false });
    const tracker3 = new Tracker({ applicationId: 'app-id-3' });
    jest.resetAllMocks();
    jest.spyOn(tracker1, 'flushQueue');
    jest.spyOn(tracker2, 'flushQueue');
    jest.spyOn(tracker3, 'flushQueue');
    globalThis.objectiv.TrackerRepository.flushAllQueues();
    expect(tracker1.flushQueue).toHaveBeenCalledTimes(1);
    expect(tracker2.flushQueue).toHaveBeenCalledTimes(1);
    expect(tracker3.flushQueue).toHaveBeenCalledTimes(1);
  });

  it('should call waitForQueue for all Tracker instances', async () => {
    const tracker1 = new Tracker({ applicationId: 'app-id-1' });
    const tracker2 = new Tracker({ applicationId: 'app-id-2' });
    const tracker3 = new Tracker({ applicationId: 'app-id-3' });
    jest.resetAllMocks();
    jest.spyOn(tracker1, 'waitForQueue');
    jest.spyOn(tracker2, 'waitForQueue');
    jest.spyOn(tracker3, 'waitForQueue');
    expect(await globalThis.objectiv.TrackerRepository.waitForAllQueues()).toBe(true);
    expect(tracker1.waitForQueue).toHaveBeenCalledTimes(1);
    expect(tracker2.waitForQueue).toHaveBeenCalledTimes(1);
    expect(tracker3.waitForQueue).toHaveBeenCalledTimes(1);
  });

  describe('Without developer tools', () => {
    let objectivGlobal = globalThis.objectiv;

    beforeEach(() => {
      jest.clearAllMocks();
      globalThis.objectiv.devTools = undefined;
    });

    afterEach(() => {
      globalThis.objectiv = objectivGlobal;
    });

    it('should return silently when adding an already existing instance', () => {
      new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' });
      new Tracker({ applicationId: 'tracker-1' });
      expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(1);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should return silently when attempting to delete the default tracker', () => {
      new Tracker({ applicationId: 'app-id-1' });
      new Tracker({ applicationId: 'app-id-2' });
      expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(2);
      expect(globalThis.objectiv.TrackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
      globalThis.objectiv.TrackerRepository.delete('app-id-1');
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should return silently when attempting to get a tracker instance from an empty repository', () => {
      expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(0);
      expect(globalThis.objectiv.TrackerRepository.get()).toBeUndefined();
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should return silently when attempting to set a default Tracker that does not exist', () => {
      new Tracker({ applicationId: 'app-id-1' });
      new Tracker({ applicationId: 'app-id-2' });
      expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(2);
      globalThis.objectiv.TrackerRepository.setDefault('app-id-3');
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should return silently when attempting to get a Tracker instance that does not exist', () => {
      new Tracker({ applicationId: 'app-id-1' });
      new Tracker({ applicationId: 'app-id-2' });
      expect(globalThis.objectiv.TrackerRepository.trackersMap.size).toBe(2);
      globalThis.objectiv.TrackerRepository.get('app-id-3');
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
