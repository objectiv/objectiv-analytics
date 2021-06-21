import { ContextResolver, ResolvableContext } from './ContextResolver';
import { LocalStorageSessionRepository, SessionRepositoryInterface } from './session-repository';
import { StackDecorator } from './StackDecorator';
import { Context } from './contexts';

const CONTEXT_RESOLVE_TIMEOUT = 5000;

export interface TrackerEvent {
  event: string;
  global_contexts?: ResolvableContext[];
  location_stack?: ResolvableContext[];
}

export interface ResolvedTrackerEvent {
  event: string;
  global_contexts?: Context[];
  location_stack?: Context[];
}

export interface TrackerInterface {
  trackEvent(event: TrackerEvent): Promise<void>;
  withContexts(globalContexts: ResolvableContext[], locationStack: ResolvableContext[]): TrackerInterface;
  withGlobalContexts(globalContexts: ResolvableContext[]): TrackerInterface;
  withLocationStack(locationStack: ResolvableContext[]): TrackerInterface;
}

export type TrackerConfiguration = {
  endpoint: string;
  sessionRepository?: SessionRepositoryInterface;
  debug?: boolean;
};

export class Tracker implements TrackerInterface {
  private readonly endpoint: string;
  protected readonly contextResolver: ContextResolver;
  private readonly sessionRepository: SessionRepositoryInterface;
  private readonly debug: boolean;

  constructor(configuration: TrackerConfiguration) {
    this.endpoint = configuration.endpoint;
    this.sessionRepository = configuration.sessionRepository ?? new LocalStorageSessionRepository();
    this.contextResolver = new ContextResolver(CONTEXT_RESOLVE_TIMEOUT);
    this.debug = configuration.debug ?? false;
  }

  async resolveEvent(event: TrackerEvent): Promise<ResolvedTrackerEvent> {
    return {
      ...event,
      global_contexts: await this.contextResolver.resolve(event.global_contexts ?? []),
      location_stack: await this.contextResolver.resolve(event.location_stack ?? []),
    };
  }

  async trackEvent(event: TrackerEvent) {
    const resolvedEvent = await this.resolveEvent(event);

    if (this.debug) {
      console.log('Tracking event', resolvedEvent);
    }

    await fetch(this.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'text/plain',
//        'X-Session-Id': await this.sessionRepository.getOrCreateSessionId(),
      },
      body: JSON.stringify([resolvedEvent]),
      // set cookies in cross-origin requests too (e.g. a request to a different port number)
      credentials: 'include',
    });
  }

  withContexts(globalContexts: ResolvableContext[], locationStack: ResolvableContext[]) {
    return new StackDecorator(this, globalContexts, locationStack);
  }

  withGlobalContexts(globalContexts: ResolvableContext[]) {
    return new StackDecorator(this, globalContexts, []);
  }

  withLocationStack(locationStack: ResolvableContext[]) {
    return new StackDecorator(this, [], locationStack);
  }
}
