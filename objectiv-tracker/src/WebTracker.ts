import {
  createDeviceContext,
  createWebDocumentContext,
  DEVICE_CONTEXT_TYPE,
  WEB_DOCUMENT_CONTEXT_TYPE,
} from './contexts';
import { Tracker, TrackerConfiguration, TrackerEvent } from './Tracker';
import { ResolvableContext } from './ContextResolver';
import { trackDocumentLoaded } from './events';
import { documentAvailable, navigatorAvailable } from './utils';

export type WebTrackerConfiguration = TrackerConfiguration & {
  id: string;
  trackWebDocument?: boolean;
  trackDevice?: boolean;
};

export class WebTracker extends Tracker {
  private readonly id: string;
  private readonly trackWebDocument: boolean;
  private readonly trackDevice: boolean;

  constructor(configuration: WebTrackerConfiguration) {
    super(configuration);
    this.id = configuration.id;
    this.trackWebDocument = configuration.trackWebDocument ?? documentAvailable;
    this.trackDevice = configuration.trackDevice ?? navigatorAvailable;

    if (this.trackWebDocument) {
      trackDocumentLoaded(this);
    }
  }

  async trackEvent(event: TrackerEvent) {
    let globalContexts: ResolvableContext[] = event.global_contexts ?? [];
    let locationStack: ResolvableContext[] = event.location_stack ?? [];

    // Resolve event early so we may validate its contexts
    const resolvedEvent = await this.resolveEvent(event);

    // Automatically tracked Location Contexts
    if (this.trackWebDocument) {
      // TODO move these checks to a Validation class
      if (resolvedEvent.location_stack.find((ctx) => ctx._context_type === WEB_DOCUMENT_CONTEXT_TYPE)) {
        throw new Error('WebDocumentContext: either disable `trackWebDocument` or remove it from the Location Stack');
      }

      // TODO make a document factory that validates if window.document is available
      locationStack.unshift(createWebDocumentContext({ id: this.id, href: window.document.location.href }));
    }

    // Automatically tracked Global Contexts
    if (this.trackDevice) {
      // TODO move these checks to a Validation class
      if (resolvedEvent.global_contexts.find((ctx) => ctx._context_type === DEVICE_CONTEXT_TYPE)) {
        throw new Error('DeviceContext: either disable `trackDevice` or remove it from Global Contexts');
      }

      // TODO make a document factory that validates if window.navigator is available
      globalContexts.push(createDeviceContext({ userAgent: window.navigator.userAgent }));
    }

    await super.trackEvent({
      ...resolvedEvent,
      global_contexts: globalContexts,
      location_stack: locationStack,
    });
  }
}
