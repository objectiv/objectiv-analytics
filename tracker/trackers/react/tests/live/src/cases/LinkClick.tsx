import { NavLink } from 'react-router-dom';
import { makeLinkContext, ReactTracker, trackLinkClick } from '@objectiv/tracker-react';
import { useMirage } from '../useMirage';

export const urlSlug = 'track-link-click';
export const menuLabel = 'trackLinkClick';
export const trackerInstance = new ReactTracker({ endpoint: '/endpoint' });

export function Component() {
  const id = 'test-link';
  const href = `/${urlSlug}?t=${Date.now()}#${Math.random().toString(36).substring(7)}`;
  const text = 'Track Link Click';

  useMirage();

  return (
    <NavLink to={href} onClick={() => trackLinkClick(makeLinkContext({ id, href, text }), trackerInstance)}>
      {text}
    </NavLink>
  );
}
