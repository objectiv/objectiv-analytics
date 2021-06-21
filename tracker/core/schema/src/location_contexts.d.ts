import { AbstractActionContext, AbstractItemContext, AbstractSectionContext } from './abstracts';

/**
 * Sections
 */
export interface SectionContext extends AbstractSectionContext {
  readonly _context_type: 'SectionContext';
}

export interface WebDocumentContext extends AbstractSectionContext {
  readonly _context_type: 'WebDocumentContext';
  url: string;
}

export interface ScreenContext extends AbstractSectionContext {
  readonly _context_type: 'ScreenContext';
  screen: string;
}

export interface ExpandableSectionContext extends AbstractSectionContext {
  readonly _context_type: 'ExpandableSectionContext';
}

export interface MediaPlayerContext extends AbstractSectionContext {
  readonly _context_type: 'MediaPlayerContext';
}

export interface NavigationContext extends AbstractSectionContext {
  readonly _context_type: 'NavigationContext';
}

export interface OverlayContext extends AbstractSectionContext {
  readonly _context_type: 'OverlayContext';
}

/**
 * Items
 */
export interface ItemContext extends AbstractItemContext {
  readonly _context_type: 'ItemContext';
}

export interface InputContext extends AbstractItemContext {
  readonly _context_type: 'InputContext';
}

/**
 * Actions
 */
export interface ActionContext extends AbstractActionContext {
  readonly _context_type: 'ActionContext';
}

export interface ButtonContext extends AbstractActionContext {
  readonly _context_type: 'ButtonContext';
}

export interface LinkContext extends AbstractActionContext {
  readonly _context_type: 'LinkContext';
}
