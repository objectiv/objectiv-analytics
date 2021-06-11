import { makeWebDocumentContext, Tracker, TrackerEvent, TrackerPlugin } from '@objectiv/tracker-core';
import { trackURLChangedEvent } from './URLChangedEvent';

/**
 * WebDocumentContextConfig allows to optionally specify a custom ID for the WebDocumentContext
 */
export type WebDocumentContextPluginConfig = {
  documentContextId?: string;
};

/**
 * The WebDocumentContext Plugin gathers the current URL from the main document using the Location API.
 * It implements the `run` method. This ensures the URL is retrieved before each Event is sent.
 */
export class WebDocumentContextPlugin implements TrackerPlugin {
  readonly pluginName = `WebDocumentContextPlugin`;
  readonly documentContextId: string;

  /**
   * Specifying a custom ID may be useful when dealing with sub-Documents. Eg: to treat them as a single Document.
   * If no ID is specified the document's `nodeName` is used.
   */
  constructor(config?: WebDocumentContextPluginConfig) {
    this.documentContextId = config?.documentContextId ?? document.nodeName;
  }

  /**
   * Initializes the URLChangedEvent listener
   */
  initialize(tracker: Tracker): void {
    trackURLChangedEvent(tracker);
  }

  /**
   * Generate a fresh WebDocumentContext before each TrackerEvent is handed over to the TrackerTransport.
   */
  beforeTransport(event: TrackerEvent): void {
    const webDocumentContext = makeWebDocumentContext({
      id: this.documentContextId,
      url: document.location.href,
    });
    event.locationStack.push(webDocumentContext);
  }
}
