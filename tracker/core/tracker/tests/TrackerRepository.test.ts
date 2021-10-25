import { Tracker, TrackerRepository } from '../src';
import { mockConsole } from './mocks/MockConsole';

describe('TrackerRepository', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });
  beforeEach(() => {
    jest.spyOn(console, 'error');
  });

  it('should console.error when attempting to get a Tracker from an empty TrackerRepository', () => {
    const trackerRepository = new TrackerRepository();
    expect(trackerRepository.trackersMap.size).toBe(0);
    expect(trackerRepository.get()).toBeUndefined();
    expect(console.error).toHaveBeenCalledWith('｢objectiv:TrackerRepository｣ There are no Trackers.');
  });

  it('should console.error when attempting to set a default Tracker that does not exist', () => {
    const trackerRepository = new TrackerRepository();
    trackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
    expect(trackerRepository.trackersMap.size).toBe(2);
    trackerRepository.setDefault('app-id-3');
    expect(console.error).toHaveBeenCalledWith('｢objectiv:TrackerRepository｣ Tracker `app-id-3` not found.');
  });

  it('should make only the first added new Tracker the default tracker', () => {
    const trackerRepository = new TrackerRepository();
    trackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id-3' }));
    expect(trackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
  });

  it('should not allow deleting the default Tracker when there are multiple trackers', () => {
    const trackerRepository = new TrackerRepository();
    trackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
    expect(trackerRepository.trackersMap.size).toBe(2);
    expect(trackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
    trackerRepository.delete('app-id-1');
    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenCalledWith(
      '｢objectiv:TrackerRepository｣ `app-id-1` is the default Tracker. Please set another as default before deleting it.'
    );
    expect(trackerRepository.trackersMap.size).toBe(2);
    expect(trackerRepository.defaultTracker?.applicationId).toBe('app-id-1');
    trackerRepository.setDefault('app-id-2');
    trackerRepository.delete('app-id-1');
    expect(trackerRepository.trackersMap.size).toBe(1);
    expect(trackerRepository.defaultTracker?.applicationId).toBe('app-id-2');
  });

  it('should add a new Tracker in the trackersMap', () => {
    const trackerRepository = new TrackerRepository();
    trackerRepository.add(new Tracker({ applicationId: 'app-id' }));
    expect(trackerRepository.trackersMap.size).toBe(1);
    expect(trackerRepository.get()).toBeInstanceOf(Tracker);
    expect(trackerRepository.get()?.applicationId).toBe('app-id');
    expect(console.error).not.toHaveBeenCalled();
  });

  it('should delete an existing Tracker from the trackersMap', () => {
    const trackerRepository = new TrackerRepository();
    trackerRepository.add(new Tracker({ applicationId: 'app-id' }));
    expect(trackerRepository.trackersMap.size).toBe(1);
    expect(trackerRepository.get()).toBeInstanceOf(Tracker);
    expect(trackerRepository.get()?.applicationId).toBe('app-id');
    expect(console.error).not.toHaveBeenCalled();
    trackerRepository.delete('app-id');
    expect(trackerRepository.trackersMap.size).toBe(0);
    expect(console.error).not.toHaveBeenCalled();
  });

  it('should create three new Trackers and get should return the first one', () => {
    const trackerRepository = new TrackerRepository();
    trackerRepository.add(new Tracker({ applicationId: 'app-id-1' }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id-2' }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id-3' }));
    expect(trackerRepository.trackersMap.size).toBe(3);
    expect(trackerRepository.get()?.applicationId).toBe('app-id-1');
    expect(trackerRepository.get('app-id-1')?.applicationId).toBe('app-id-1');
    expect(trackerRepository.get('app-id-2')?.applicationId).toBe('app-id-2');
    expect(trackerRepository.get('app-id-3')?.applicationId).toBe('app-id-3');
  });

  it('should allow creating multiple Trackers for the same application', () => {
    const trackerRepository = new TrackerRepository();
    trackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-2' }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-3' }));
    expect(trackerRepository.trackersMap.size).toBe(3);
    expect(trackerRepository.get('app-id-1')).toBeUndefined();
    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenCalledWith('｢objectiv:TrackerRepository｣ Tracker `app-id-1` not found.');
    expect(trackerRepository.get('tracker-1')?.applicationId).toBe('app-id');
    expect(trackerRepository.get('tracker-2')?.applicationId).toBe('app-id');
    expect(trackerRepository.get('tracker-3')?.applicationId).toBe('app-id');
  });

  it('should not allow overwriting an existing Tracker instance', () => {
    const trackerRepository = new TrackerRepository();
    trackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' }));
    trackerRepository.add(new Tracker({ applicationId: 'tracker-1' }));
    expect(trackerRepository.trackersMap.size).toBe(1);
    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenCalledWith('｢objectiv:TrackerRepository｣ Tracker `tracker-1` already exists.');
    trackerRepository.add(new Tracker({ applicationId: 'app-id', trackerId: 'tracker-1' }));
    expect(trackerRepository.trackersMap.size).toBe(1);
    expect(console.error).toHaveBeenCalledTimes(2);
    expect(console.error).toHaveBeenNthCalledWith(
      2,
      '｢objectiv:TrackerRepository｣ Tracker `tracker-1` already exists.'
    );
  });

  it('should activate all inactive Tracker instances', () => {
    const trackerRepository = new TrackerRepository();
    trackerRepository.add(new Tracker({ applicationId: 'app-id-1', active: false, console: mockConsole }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id-2', console: mockConsole }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id-3', active: false, console: mockConsole }));
    jest.resetAllMocks();
    trackerRepository.activateAll();
    expect(mockConsole.log).toHaveBeenCalledTimes(2);
    expect(mockConsole.log).toHaveBeenNthCalledWith(
      1,
      '%c｢objectiv:Tracker:app-id-1｣ New state: active',
      'font-weight: bold'
    );
    expect(mockConsole.log).toHaveBeenNthCalledWith(
      2,
      '%c｢objectiv:Tracker:app-id-3｣ New state: active',
      'font-weight: bold'
    );
  });

  it('should deactivate all active Tracker instances', () => {
    const trackerRepository = new TrackerRepository();
    trackerRepository.add(new Tracker({ applicationId: 'app-id-1', console: mockConsole }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id-2', active: false, console: mockConsole }));
    trackerRepository.add(new Tracker({ applicationId: 'app-id-3', console: mockConsole }));
    jest.resetAllMocks();
    trackerRepository.deactivateAll();
    expect(mockConsole.log).toHaveBeenCalledTimes(2);
    expect(mockConsole.log).toHaveBeenNthCalledWith(
      1,
      '%c｢objectiv:Tracker:app-id-1｣ New state: inactive',
      'font-weight: bold'
    );
    expect(mockConsole.log).toHaveBeenNthCalledWith(
      2,
      '%c｢objectiv:Tracker:app-id-3｣ New state: inactive',
      'font-weight: bold'
    );
  });

  it('should call flushQueue for all active Tracker instances', () => {
    const trackerRepository = new TrackerRepository();
    const tracker1 = new Tracker({ applicationId: 'app-id-1', console: mockConsole });
    const tracker2 = new Tracker({ applicationId: 'app-id-2', active: false, console: mockConsole });
    const tracker3 = new Tracker({ applicationId: 'app-id-3', console: mockConsole });
    trackerRepository.add(tracker1);
    trackerRepository.add(tracker2);
    trackerRepository.add(tracker3);
    jest.resetAllMocks();
    jest.spyOn(tracker1, 'flushQueue');
    jest.spyOn(tracker2, 'flushQueue');
    jest.spyOn(tracker3, 'flushQueue');
    trackerRepository.flushAllQueues();
    expect(tracker1.flushQueue).toHaveBeenCalledTimes(1);
    expect(tracker2.flushQueue).toHaveBeenCalledTimes(1);
    expect(tracker3.flushQueue).toHaveBeenCalledTimes(1);
  });
});
