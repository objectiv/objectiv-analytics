/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { Tracker, TrackerRepository } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackerRepository', () => {
  beforeEach(() => {
    TrackerRepository.trackersMap.clear();
    TrackerRepository.defaultTracker = undefined;
    jest.resetAllMocks();
  });

  it('should console.error when attempting to get a Tracker from an empty TrackerRepository', () => {
    expect(TrackerRepository.trackersMap.size).toBe(0);
    expect(TrackerRepository.get()).toBeUndefined();
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith('｢objectiv:TrackerRepository｣ There are no Trackers.');
  });

  it('should console.error when attempting to set a default Tracker that does not exist', () => {
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
    expect(TrackerRepository.trackersMap.size).toBe(2);
    TrackerRepository.setDefault('app-id-3');
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ Tracker `app-id-3` not found.'
    );
  });

  it('should make only the first added new Tracker the default tracker', () => {
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-3' }));
    expect(TrackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
  });

  it('should not allow deleting the default Tracker when there are multiple trackers', () => {
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
    expect(TrackerRepository.trackersMap.size).toBe(2);
    expect(TrackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
    TrackerRepository.delete('app-id-1');
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ `app-id-1` is the default Tracker. Please set another as default before deleting it.'
    );
    expect(TrackerRepository.trackersMap.size).toBe(2);
    expect(TrackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
    TrackerRepository.setDefault('app-id-2');
    TrackerRepository.delete('app-id-1');
    expect(TrackerRepository.trackersMap.size).toBe(1);
    expect(TrackerRepository.defaultTracker?.applicationId).toBe('app-id-2');
  });

  it('should add a new Tracker in the trackersMap', () => {
    TrackerRepository.add(new Tracker({ applicationId: 'app-id' }));
    expect(TrackerRepository.trackersMap.size).toBe(1);
    expect(TrackerRepository.get()).toBeInstanceOf(Tracker);
    expect(TrackerRepository.get()?.applicationId).toBe('app-id');
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
  });

  it('should delete an existing Tracker from the trackersMap', () => {
    TrackerRepository.add(new Tracker({ applicationId: 'app-id' }));
    expect(TrackerRepository.trackersMap.size).toBe(1);
    expect(TrackerRepository.get()).toBeInstanceOf(Tracker);
    expect(TrackerRepository.get()?.applicationId).toBe('app-id');
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    TrackerRepository.delete('app-id');
    expect(TrackerRepository.trackersMap.size).toBe(0);
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
  });

  it('should create three new Trackers and get should return the first one', () => {
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-3' }));
    expect(TrackerRepository.trackersMap.size).toBe(3);
    expect(TrackerRepository.get()?.applicationId).toBe('app-id-1');
    expect(TrackerRepository.get('app-id-1')?.applicationId).toBe('app-id-1');
    expect(TrackerRepository.get('app-id-2')?.applicationId).toBe('app-id-2');
    expect(TrackerRepository.get('app-id-3')?.applicationId).toBe('app-id-3');
  });

  it('should allow creating multiple Trackers for the same application', () => {
    TrackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' }));
    TrackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-2' }));
    TrackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-3' }));
    expect(TrackerRepository.trackersMap.size).toBe(3);
    expect(TrackerRepository.get('app-id-1')).toBeUndefined();
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ Tracker `app-id-1` not found.'
    );
    expect(TrackerRepository.get('tracker-1')?.applicationId).toBe('app-id');
    expect(TrackerRepository.get('tracker-2')?.applicationId).toBe('app-id');
    expect(TrackerRepository.get('tracker-3')?.applicationId).toBe('app-id');
  });

  it('should not allow overwriting an existing Tracker instance', () => {
    TrackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' }));
    TrackerRepository.add(new Tracker({ applicationId: 'tracker-1' }));
    expect(TrackerRepository.trackersMap.size).toBe(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ Tracker `tracker-1` already exists.'
    );
    TrackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' }));
    expect(TrackerRepository.trackersMap.size).toBe(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      2,
      '｢objectiv:TrackerRepository｣ Tracker `tracker-1` already exists.'
    );
  });

  it('should activate all inactive Tracker instances', () => {
    const tracker1 = new Tracker({ applicationId: 'app-id-1', active: false });
    tracker1.plugins.plugins = [];
    const tracker2 = new Tracker({ applicationId: 'app-id-2' });
    tracker2.plugins.plugins = [];
    const tracker3 = new Tracker({ applicationId: 'app-id-3', active: false });
    tracker3.plugins.plugins = [];
    TrackerRepository.add(tracker1);
    TrackerRepository.add(tracker2);
    TrackerRepository.add(tracker3);
    jest.resetAllMocks();
    TrackerRepository.activateAll();
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
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-2', active: false }));
    TrackerRepository.add(new Tracker({ applicationId: 'app-id-3' }));
    jest.resetAllMocks();
    TrackerRepository.deactivateAll();
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
    TrackerRepository.add(tracker1);
    TrackerRepository.add(tracker2);
    TrackerRepository.add(tracker3);
    jest.resetAllMocks();
    jest.spyOn(tracker1, 'flushQueue');
    jest.spyOn(tracker2, 'flushQueue');
    jest.spyOn(tracker3, 'flushQueue');
    TrackerRepository.flushAllQueues();
    expect(tracker1.flushQueue).toHaveBeenCalledTimes(1);
    expect(tracker2.flushQueue).toHaveBeenCalledTimes(1);
    expect(tracker3.flushQueue).toHaveBeenCalledTimes(1);
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

    it('should return silently when adding an already existing instance', () => {
      TrackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' }));
      TrackerRepository.add(new Tracker({ applicationId: 'tracker-1' }));
      expect(TrackerRepository.trackersMap.size).toBe(1);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should return silently when attempting to delete the default tracker', () => {
      TrackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
      TrackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
      expect(TrackerRepository.trackersMap.size).toBe(2);
      expect(TrackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
      TrackerRepository.delete('app-id-1');
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should return silently when attempting to get a tracker instance from an empty repository', () => {
      expect(TrackerRepository.trackersMap.size).toBe(0);
      expect(TrackerRepository.get()).toBeUndefined();
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should return silently when attempting to set a default Tracker that does not exist', () => {
      TrackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
      TrackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
      expect(TrackerRepository.trackersMap.size).toBe(2);
      TrackerRepository.setDefault('app-id-3');
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should return silently when attempting to get a Tracker instance that does not exist', () => {
      TrackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
      TrackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
      expect(TrackerRepository.trackersMap.size).toBe(2);
      TrackerRepository.get('app-id-3');
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
