import { TrackingAttributes } from './structs';
import { TrackingAttribute } from './TrackingAttributes';

/**
 * The type of Elements the type guards can work with
 */
export type GuardElement = Node | EventTarget | null;

/**
 * A Trackable Element is an HTMLElement or an SVGElement
 */
export type TrackableElement = HTMLElement | SVGElement;

/**
 * A type guard to determine if a the given Element is an HTMLElement or SVGElement.
 * In general we can only track Elements supporting dataset attributes.
 */
export const isTrackableElement = (element: GuardElement): element is TrackableElement =>
  element instanceof HTMLElement || element instanceof SVGElement;

/**
 * A Tracked Element is a TrackableElement with our TrackingAttributes
 */
export type TrackedElement = TrackableElement & { dataset: TrackingAttributes };

/**
 * A type guard to determine if the given Element is a TrackableElement decorated with TrackingAttributes.
 * Note: For performance and simplicity we only check if `context` is present. Assume all other attributes are there.
 */
export const isTrackedElement = (element: GuardElement): element is TrackedElement =>
  isTrackableElement(element) && element.hasAttribute(TrackingAttribute.context);

/**
 * A Children Tracking Element is a TrackableElement with our ChildrenTrackingAttributes
 */
export type ChildrenTrackingElement = TrackableElement & { dataset: TrackingAttributes };

/**
 * A type guard to determine if the given Element is a TrackableElement decorated with ChildrenTrackingAttributes.
 */
export const isChildrenTrackingElement = (element: GuardElement): element is ChildrenTrackingElement =>
  isTrackableElement(element) && element.hasAttribute(TrackingAttribute.trackChildren);

/**
 * A Custom Parent Tracking Element is a TrackedElement with the TrackingAttribute.parentElementId
 */
export type CustomParentTrackedElement = TrackableElement & { dataset: TrackingAttributes };

/**
 * A type guard to determine if the given Element is a TrackableElement decorated with ChildrenTrackingAttributes.
 */
export const isCustomParentTrackedElement = (element: GuardElement): element is CustomParentTrackedElement =>
  isTrackedElement(element) && element.hasAttribute(TrackingAttribute.parentElementId);
