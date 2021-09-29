import { ChildrenTaggingAttributes, TaggingAttributes } from './structs';
import { TaggingAttribute } from './TaggingAttribute';

/**
 * The type of Elements the type guards can work with
 */
export type GuardElement = Node | EventTarget | null;

/**
 * A Trackable Element is an HTMLElement or an SVGElement
 */
export type TaggableElement = HTMLElement | SVGElement;

/**
 * A type guard to determine if a the given Element is an HTMLElement or SVGElement.
 * In general we can only tag Elements supporting dataset attributes.
 */
export const isTaggableElement = (element: GuardElement): element is TaggableElement =>
  element instanceof HTMLElement || element instanceof SVGElement;

/**
 * A TaggedElement is a TaggableElement already decorated with our TaggingAttributes
 */
export type TaggedElement = TaggableElement & { dataset: TaggingAttributes };

/**
 * A type guard to determine if the given Element is a TaggableElement decorated with TaggingAttributes.
 * Note: For performance and simplicity we only check if `context` is present. Assume all other attributes are there.
 */
export const isTaggedElement = (element: GuardElement): element is TaggedElement =>
  isTaggableElement(element) && element.hasAttribute(TaggingAttribute.context);

/**
 * A ChildrenTaggingElement is a TaggableElement already decorated with our ChildrenTaggingAttributes
 */
export type ChildrenTaggingElement = TaggableElement & { dataset: ChildrenTaggingAttributes };

/**
 * A type guard to determine if the given Element is a TaggableElement decorated with ChildrenTaggingAttributes.
 */
export const isChildrenTaggingElement = (element: GuardElement): element is ChildrenTaggingElement =>
  isTaggableElement(element) && element.hasAttribute(TaggingAttribute.tagChildren);

/**
 * A CustomParentTaggedElement is a TaggedElement with the TaggingAttribute.parentElementId
 */
export type CustomParentTaggedElement = TaggableElement & {
  dataset: Pick<TaggingAttributes, TaggingAttribute.parentElementId>;
};

/**
 * A type guard to determine if the given Element is a TaggableElement decorated with TaggingAttributes.parentElementId.
 */
export const isCustomParentTaggedElement = (element: GuardElement): element is CustomParentTaggedElement =>
  isTaggedElement(element) && element.hasAttribute(TaggingAttribute.parentElementId);
