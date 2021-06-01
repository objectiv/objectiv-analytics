import { TrackerEvent } from "@objectiv/core";
import { CustomContext } from "./CustomContext";

export type CustomEvent = TrackerEvent & {
  eventName: 'CustomEvent';
  requiresContext: CustomContext
}
