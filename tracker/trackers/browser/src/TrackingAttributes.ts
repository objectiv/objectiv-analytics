import { boolean, defaulted, define, Infer, is, literal, object, optional, string, union } from 'superstruct';
import { validate, v4 } from 'uuid';
import { LocationContext } from './Contexts';

/**
 * The possible values of the `trackVisibility` TrackingAttribute.
 */
export const TrackingAttributeVisibilityAuto = object({ mode: literal('auto') });
export type TrackingAttributeVisibilityAuto = Infer<typeof TrackingAttributeVisibilityAuto>;

export const TrackingAttributeVisibilityManual = object({ mode: literal('manual'), isVisible: boolean() });
export type TrackingAttributeVisibilityManual = Infer<typeof TrackingAttributeVisibilityManual>;

export const TrackingAttributeVisibility = union([TrackingAttributeVisibilityAuto, TrackingAttributeVisibilityManual]);
export type TrackingAttributeVisibility = Infer<typeof TrackingAttributeVisibility>;

/**
 * All the attributes that are added to a DOM Element to make it trackable
 */
export enum ElementTrackingAttribute {
  // A unique identifier used internally to pinpoint to a specific instance of a tracked element
  elementId = 'data-objectiv-element-id',

  // DOM traversing to rebuild Locations is not always possible, eg: Portals. This allows specifying a parent Element.
  parentElementId = 'data-objectiv-parent-element-id',

  // A serialized instance of an Objectiv Context
  context = 'data-objectiv-context',

  // Track click events for this tracked element
  trackClicks = 'data-objectiv-track-clicks',

  // Track blur events for this tracked element
  trackBlurs = 'data-objectiv-track-blurs',

  // Determines how we will track visibility events for this tracked element.
  trackVisibility = 'data-objectiv-track-visibility',
}

/**
 * All the attributes that are added to a DOM Element that tracks its children via querySelector
 */
export enum ChildrenTrackingAttribute {
  // A list of serialized ChildTrackingQuery objects
  trackChildren = 'data-objectiv-track-children',
}

/**
 * A custom Struct describing v4 UUIDs
 */
export const Uuid = define('Uuid', (value: any) => validate(value));

/**
 * Custom Structs describing stringified booleans
 */
export const StringTrue = define('StringTrue', (value: any) => value === 'true');
export const StringFalse = define('StringFalse', (value: any) => value === 'false');
export const StringBoolean = define('StringBoolean', (value: any) => is(value, union([StringTrue, StringFalse])));

/**
 * The object that `track` calls return
 */
export const ElementTrackingAttributes = object({
  [ElementTrackingAttribute.elementId]: Uuid,
  [ElementTrackingAttribute.parentElementId]: optional(Uuid),
  [ElementTrackingAttribute.context]: LocationContext,
  [ElementTrackingAttribute.trackClicks]: optional(boolean()),
  [ElementTrackingAttribute.trackBlurs]: optional(boolean()),
  [ElementTrackingAttribute.trackVisibility]: optional(TrackingAttributeVisibility),
});
export type ElementTrackingAttributes = Infer<typeof ElementTrackingAttributes>;

/**
 * The object that `track` calls return, stringified
 */
export const StringifiedElementTrackingAttributes = object({
  [ElementTrackingAttribute.elementId]: defaulted(Uuid, () => v4()),
  [ElementTrackingAttribute.parentElementId]: optional(Uuid),
  [ElementTrackingAttribute.context]: string(),
  [ElementTrackingAttribute.trackClicks]: optional(StringBoolean),
  [ElementTrackingAttribute.trackBlurs]: optional(StringBoolean),
  [ElementTrackingAttribute.trackVisibility]: optional(string()),
});
export type StringifiedElementTrackingAttributes = Infer<typeof StringifiedElementTrackingAttributes>;

/**
 * The object that `trackChildren` calls return
 */
export type ChildrenTrackingAttributes = {
  [ChildrenTrackingAttribute.trackChildren]: string[];
};
