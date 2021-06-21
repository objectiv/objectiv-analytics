import {
  MemoryQueue,
  Tracker,
  TrackerEvent,
  QueuedTransport,
  TransportGroup,
  TransportSwitch,
  ContextsConfig,
} from '../src';
import { LogTransport, UnusableTransport } from './mocks';
import { ConfigurableMockTransport } from './mocks/ConfigurableMockTransport';

const testEventName = 'test-event';
const testContexts: ContextsConfig = {
  location_stack: [{ __location_context: true, _context_type: 'section', id: 'test' }],
  global_contexts: [{ __global_context: true, _context_type: 'global', id: 'test' }],
};
const testEvent = new TrackerEvent({ event: testEventName, ...testContexts });

describe('TransportSwitch', () => {
  it('should not pick any TrackerTransport', () => {
    const transport1 = new UnusableTransport();
    const transport2 = new LogTransport();
    transport2.isUsable = () => false;

    expect(transport1.isUsable()).toBe(false);
    expect(transport2.isUsable()).toBe(false);

    spyOn(transport1, 'handle');
    spyOn(transport2, 'handle');

    const transports = new TransportSwitch(transport1, transport2);
    expect(transports.firstUsableTransport).toBe(undefined);
    expect(transports.isUsable()).toBe(false);

    expect(() => {
      transports.handle(testEvent);
    }).toThrow();

    expect(transport1.handle).not.toHaveBeenCalled();
    expect(transport2.handle).not.toHaveBeenCalled();
  });

  it('should pick the second TrackerTransport', () => {
    const transport1 = new UnusableTransport();
    const transport2 = new LogTransport();

    expect(transport1.isUsable()).toBe(false);
    expect(transport2.isUsable()).toBe(true);

    spyOn(transport1, 'handle');
    spyOn(transport2, 'handle');

    const transports = new TransportSwitch(transport1, transport2);
    expect(transports.firstUsableTransport).toBe(transport2);
    expect(transports.isUsable()).toBe(true);

    const testTracker = new Tracker({ transport: transports });

    testTracker.trackEvent(testEvent);

    expect(transport1.handle).not.toHaveBeenCalled();
    expect(transport2.handle).toHaveBeenCalledWith(testEvent);
  });
});

describe('TransportGroup', () => {
  it('should not handle any TrackerTransport', () => {
    const transport1 = new UnusableTransport();
    const transport2 = new LogTransport();
    transport2.isUsable = () => false;

    expect(transport1.isUsable()).toBe(false);
    expect(transport2.isUsable()).toBe(false);

    spyOn(transport1, 'handle');
    spyOn(transport2, 'handle');

    const transports = new TransportGroup(transport1, transport2);
    expect(transports.usableTransports).toStrictEqual([]);
    expect(transports.isUsable()).toBe(false);

    expect(() => {
      transports.handle(testEvent);
    }).toThrow();

    expect(transport1.handle).not.toHaveBeenCalled();
    expect(transport2.handle).not.toHaveBeenCalled();
  });

  it('should handle both TrackerTransport', () => {
    const transport1 = new LogTransport();
    const transport2 = new LogTransport();

    expect(transport1.isUsable()).toBe(true);
    expect(transport2.isUsable()).toBe(true);

    spyOn(transport1, 'handle');
    spyOn(transport2, 'handle');

    const transports = new TransportGroup(transport1, transport2);
    expect(transports.usableTransports).toStrictEqual([transport1, transport2]);
    expect(transports.isUsable()).toBe(true);

    const testTracker = new Tracker({ transport: transports });

    testTracker.trackEvent(testEvent);

    expect(transport1.handle).toHaveBeenCalled();
    expect(transport2.handle).toHaveBeenCalled();
  });
});

describe('TrackerTransport complex configurations', () => {
  const beacon = new ConfigurableMockTransport({ isUsable: false });
  const fetch = new ConfigurableMockTransport({ isUsable: false });
  const xmlHTTPRequest = new ConfigurableMockTransport({ isUsable: false });
  const pigeon = new ConfigurableMockTransport({ isUsable: false });
  const consoleLog = new ConfigurableMockTransport({ isUsable: false });
  const errorLog = new ConfigurableMockTransport({ isUsable: false });

  beforeEach(() => {
    beacon._isUsable = false;
    fetch._isUsable = false;
    xmlHTTPRequest._isUsable = false;
    pigeon._isUsable = false;
    consoleLog._isUsable = false;
    errorLog._isUsable = false;
    jest.clearAllMocks();
    spyOn(beacon, 'handle');
    spyOn(fetch, 'handle');
    spyOn(xmlHTTPRequest, 'handle');
    spyOn(pigeon, 'handle');
    spyOn(consoleLog, 'handle');
    spyOn(errorLog, 'handle');
  });

  it('should handle to errorLog', () => {
    errorLog._isUsable = true;
    expect(errorLog.isUsable()).toBe(true);

    const sendTransport = new TransportSwitch(beacon, fetch, xmlHTTPRequest, pigeon);
    const sendAndLog = new TransportGroup(sendTransport, consoleLog);
    const transport = new TransportSwitch(sendAndLog, errorLog);

    expect(sendTransport.isUsable()).toBe(false);
    expect(sendAndLog.isUsable()).toBe(false);
    expect(transport.isUsable()).toBe(true);

    const testTracker = new Tracker({ transport });

    testTracker.trackEvent(testEvent);

    expect(beacon.handle).not.toHaveBeenCalled();
    expect(fetch.handle).not.toHaveBeenCalled();
    expect(xmlHTTPRequest.handle).not.toHaveBeenCalled();
    expect(pigeon.handle).not.toHaveBeenCalled();
    expect(consoleLog.handle).not.toHaveBeenCalled();
    expect(errorLog.handle).toHaveBeenCalled();
  });

  it('should handle to fetch and consoleLog', () => {
    fetch._isUsable = true;
    expect(fetch.isUsable()).toBe(true);
    consoleLog._isUsable = true;
    expect(consoleLog.isUsable()).toBe(true);

    const sendTransport = new TransportSwitch(beacon, fetch, xmlHTTPRequest, pigeon);
    const sendAndLog = new TransportGroup(sendTransport, consoleLog);
    const transport = new TransportSwitch(sendAndLog, errorLog);

    expect(sendTransport.isUsable()).toBe(true);
    expect(sendAndLog.isUsable()).toBe(true);
    expect(transport.isUsable()).toBe(true);

    const testTracker = new Tracker({ transport });

    testTracker.trackEvent(testEvent);

    expect(beacon.handle).not.toHaveBeenCalled();
    expect(fetch.handle).toHaveBeenCalled();
    expect(xmlHTTPRequest.handle).not.toHaveBeenCalled();
    expect(pigeon.handle).not.toHaveBeenCalled();
    expect(consoleLog.handle).toHaveBeenCalled();
    expect(errorLog.handle).not.toHaveBeenCalled();
  });

  it('should handle to consoleLog', () => {
    consoleLog._isUsable = true;
    expect(consoleLog.isUsable()).toBe(true);

    const sendTransport = new TransportSwitch(beacon, fetch, xmlHTTPRequest, pigeon);
    const sendAndLog = new TransportGroup(sendTransport, consoleLog);
    const transport = new TransportSwitch(sendAndLog, errorLog);

    expect(sendTransport.isUsable()).toBe(false);
    expect(sendAndLog.isUsable()).toBe(true);
    expect(transport.isUsable()).toBe(true);

    const testTracker = new Tracker({ transport });

    testTracker.trackEvent(testEvent);

    expect(beacon.handle).not.toHaveBeenCalled();
    expect(fetch.handle).not.toHaveBeenCalled();
    expect(xmlHTTPRequest.handle).not.toHaveBeenCalled();
    expect(pigeon.handle).not.toHaveBeenCalled();
    expect(consoleLog.handle).toHaveBeenCalled();
    expect(errorLog.handle).not.toHaveBeenCalled();
  });
});

describe('QueuedTransport', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  it('should do nothing if the given transport is not usable', () => {
    const memoryQueue = new MemoryQueue();
    const logTransport = new UnusableTransport();

    spyOn(logTransport, 'handle');

    const testQueuedTransport = new QueuedTransport({
      queue: memoryQueue,
      transport: logTransport,
    });

    expect(testQueuedTransport.isUsable()).toBe(false);

    expect(memoryQueue.events).toHaveLength(0);
    expect(logTransport.handle).not.toHaveBeenCalled();
    expect(setInterval).toHaveBeenCalledTimes(0);
  });

  it('should queue events in the MemoryQueue and send them in batches via the LogTransport', () => {
    const memoryQueue = new MemoryQueue();
    const logTransport = new LogTransport();

    spyOn(logTransport, 'handle');

    const testQueuedTransport = new QueuedTransport({
      queue: memoryQueue,
      transport: logTransport,
    });

    expect(testQueuedTransport.isUsable()).toBe(true);

    expect(memoryQueue.events).toHaveLength(0);
    expect(logTransport.handle).not.toHaveBeenCalled();
    expect(setInterval).toHaveBeenCalledTimes(1);

    testQueuedTransport.handle(testEvent);

    expect(memoryQueue.events).toHaveLength(1);
    expect(logTransport.handle).not.toHaveBeenCalled();

    jest.runTimersToTime(memoryQueue.batchDelayMs);
    expect(memoryQueue.events).toHaveLength(0);
    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenCalledWith(testEvent);

    jest.runTimersToTime(memoryQueue.batchDelayMs);
    expect(memoryQueue.events).toHaveLength(0);
    expect(logTransport.handle).toHaveBeenCalledTimes(1);
  });
});
