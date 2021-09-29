import { ApplicationContext } from '@objectiv/schema';
import { makeApplicationContext } from './ContextFactories';
import { TrackerEvent } from './TrackerEvent';
import { TrackerPlugin } from './TrackerPlugin';

/**
 * The ApplicationContext Plugin adds an ApplicationContext as GlobalContext before events are transported.
 */
export class ApplicationContextPlugin implements TrackerPlugin {
  readonly pluginName = `ApplicationContextPlugin`;
  readonly applicationContext: ApplicationContext;

  /**
   * Generates a ApplicationContext from the given config applicationId.
   */
  constructor(config: { applicationId: string }) {
    this.applicationContext = makeApplicationContext({
      id: config.applicationId,
    });

    console.groupCollapsed(`｢objectiv:${this.pluginName}｣ Initialized`);
    console.log(`Application ID: ${config.applicationId}`);
    console.group(`Application Context:`);
    console.log(this.applicationContext);
    console.groupEnd();
    console.groupEnd();
  }

  /**
   * Add the the ApplicationContext to the Event's Global Contexts
   */
  beforeTransport(event: TrackerEvent): void {
    event.global_contexts.push(this.applicationContext);
  }

  /**
   * Make this plugin usable only if the Navigator API is available
   */
  isUsable(): boolean {
    return true;
  }
}
