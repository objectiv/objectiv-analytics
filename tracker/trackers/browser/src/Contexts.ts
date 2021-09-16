import { assign, Infer, literal, object, string, union } from 'superstruct';

/**
 * Abstract Contexts
 */
export const AbstractContext = object({
  id: string(),
  _type: string(),
});

/**
 * AbstractLocationContext
 */
export const AbstractLocationContext = assign(
  AbstractContext,
  object({
    __location_context: literal(true),
  })
);

/**
 * AbstractSectionContext
 */
export const AbstractSectionContext = assign(
  AbstractLocationContext,
  object({
    __section_context: literal(true),
  })
);

/**
 * AbstractItemContext
 */
export const AbstractItemContext = assign(
  AbstractLocationContext,
  object({
    __item_context: literal(true),
  })
);

/**
 * AbstractActionContext
 */
export const AbstractActionContext = assign(
  AbstractItemContext,
  object({
    __action_context: literal(true),
    text: string(),
  })
);

/**
 * ElementContext
 */
export const SectionContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('SectionContext'),
  })
);

/**
 * WebDocumentContext
 */
export const WebDocumentContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('WebDocumentContext'),
    url: string(),
  })
);

/**
 * ScreenContext
 */
export const ScreenContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('ScreenContext'),
    screen: string(),
  })
);

/**
 * ExpandableSectionContext
 */
export const ExpandableSectionContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('ExpandableSectionContext'),
  })
);

/**
 * MediaPlayerContext
 */
export const MediaPlayerContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('MediaPlayerContext'),
  })
);

/**
 * NavigationContext
 */
export const NavigationContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('NavigationContext'),
  })
);

/**
 * OverlayContext
 */
export const OverlayContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('OverlayContext'),
  })
);

/**
 * ItemContext
 */
export const ItemContext = assign(
  AbstractItemContext,
  object({
    _type: literal('ItemContext'),
  })
);

/**
 * InputContext
 */
export const InputContext = assign(
  AbstractItemContext,
  object({
    _type: literal('InputContext'),
  })
);

/**
 * ActionContext
 */
export const ActionContext = assign(
  AbstractActionContext,
  object({
    _type: literal('ActionContext'),
  })
);

/**
 * ButtonContext
 */
export const ButtonContext = assign(
  AbstractActionContext,
  object({
    _type: literal('ButtonContext'),
  })
);

/**
 * LinkContext
 */
export const LinkContext = assign(
  AbstractActionContext,
  object({
    _type: literal('LinkContext'),
    href: string(),
  })
);

/**
 * Custom Struct to match any LocationContext
 */
export const AnyLocationContext = union([
  SectionContext,
  WebDocumentContext,
  ScreenContext,
  ExpandableSectionContext,
  MediaPlayerContext,
  NavigationContext,
  OverlayContext,
  ItemContext,
  InputContext,
  ActionContext,
  ButtonContext,
  LinkContext,
]);
export type AnyLocationContext = Infer<typeof AnyLocationContext>;

/**
 * Struct to match any SectionContext
 */
export const AnySectionContext = union([
  SectionContext,
  WebDocumentContext,
  ScreenContext,
  ExpandableSectionContext,
  MediaPlayerContext,
  NavigationContext,
  OverlayContext,
]);
export type AnySectionContext = Infer<typeof AnySectionContext>;

/**
 * Struct to match any ItemContext
 */
export const AnyItemContext = union([ItemContext, InputContext, ActionContext, ButtonContext, LinkContext]);
export type AnyItemContext = Infer<typeof AnyItemContext>;

/**
 * Struct to match any ActionContext
 */
export const AnyActionContext = union([ActionContext, ButtonContext, LinkContext]);
export type AnyActionContext = Infer<typeof AnyActionContext>;
