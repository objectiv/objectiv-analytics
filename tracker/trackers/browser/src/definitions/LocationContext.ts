/*
 * Copyright 2021 Objectiv B.V.
 */

import { assign, Infer, literal, object, string, union } from 'superstruct';

/**
 * Abstract Context struct
 */
export const AbstractContext = object({
  id: string(),
  _type: string(),
});

/**
 * AbstractLocationContext struct
 */
export const AbstractLocationContext = assign(
  AbstractContext,
  object({
    __location_context: literal(true),
  })
);

/**
 * AbstractSectionContext struct
 */
export const AbstractSectionContext = assign(
  AbstractLocationContext,
  object({
    __section_context: literal(true),
  })
);

/**
 * AbstractItemContext struct
 */
export const AbstractItemContext = assign(
  AbstractLocationContext,
  object({
    __item_context: literal(true),
  })
);

/**
 * AbstractActionContext struct
 */
export const AbstractActionContext = assign(
  AbstractItemContext,
  object({
    __action_context: literal(true),
    text: string(),
  })
);

/**
 * ElementContext struct
 */
export const SectionContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('SectionContext'),
  })
);

/**
 * WebDocumentContext struct
 */
export const WebDocumentContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('WebDocumentContext'),
    url: string(),
  })
);

/**
 * ScreenContext struct
 */
export const ScreenContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('ScreenContext'),
    screen: string(),
  })
);

/**
 * ExpandableSectionContext struct
 */
export const ExpandableSectionContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('ExpandableSectionContext'),
  })
);

/**
 * MediaPlayerContext struct
 */
export const MediaPlayerContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('MediaPlayerContext'),
  })
);

/**
 * NavigationContext struct
 */
export const NavigationContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('NavigationContext'),
  })
);

/**
 * OverlayContext struct
 */
export const OverlayContext = assign(
  AbstractSectionContext,
  object({
    _type: literal('OverlayContext'),
  })
);

/**
 * ItemContext struct
 */
export const ItemContext = assign(
  AbstractItemContext,
  object({
    _type: literal('ItemContext'),
  })
);

/**
 * InputContext struct
 */
export const InputContext = assign(
  AbstractItemContext,
  object({
    _type: literal('InputContext'),
  })
);

/**
 * ActionContext struct
 */
export const ActionContext = assign(
  AbstractActionContext,
  object({
    _type: literal('ActionContext'),
  })
);

/**
 * ButtonContext struct
 */
export const ButtonContext = assign(
  AbstractActionContext,
  object({
    _type: literal('ButtonContext'),
  })
);

/**
 * LinkContext struct
 */
export const LinkContext = assign(
  AbstractActionContext,
  object({
    _type: literal('LinkContext'),
    href: string(),
  })
);

/**
 * Struct union to match any LocationContext
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
 * Struct union to match any SectionContext
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
 * Struct union to match any ItemContext
 */
export const AnyItemContext = union([ItemContext, InputContext, ActionContext, ButtonContext, LinkContext]);

export type AnyItemContext = Infer<typeof AnyItemContext>;

/**
 * Struct union to match any ActionContext
 */
export const AnyActionContext = union([ActionContext, ButtonContext, LinkContext]);

export type AnyActionContext = Infer<typeof AnyActionContext>;

/**
 * Struct union to match any Clickable Context, that is Action Contexts + ExpandableSectionContext
 */
export const AnyClickableContext = union([AnyActionContext, ExpandableSectionContext]);

export type AnyClickableContext = Infer<typeof AnyClickableContext>;

/**
 * Struct union to match any Showable Context, that is Overlays and ExpandableSectionContext
 */
export const AnyShowableContext = union([OverlayContext, ExpandableSectionContext]);

export type AnyShowableContext = Infer<typeof AnyShowableContext>;
