import { NavLink } from "react-router-dom";
import { makeLinkContext, trackLinkClick, useTracker } from "@objectiv/tracker-react";

export const urlSlug = 'track-link-click'
export const menuLabel = 'trackLinkClick'

export function Component() {
  const tracker = useTracker();

  const id = 'test-link';
  const href = `/${urlSlug}?t=${Date.now()}#${Math.random().toString(36).substring(7)}`;
  const text = 'Track Link Click';

  return (
    <NavLink
      to={href}
      onClick={
        () => trackLinkClick(makeLinkContext({id, href, text}), tracker)
      }>
      Track Link Click
    </NavLink>
  );
}
