import { Case } from "./App";
import { NavLink } from "react-router-dom";

export default function MenuItem({ urlSlug, menuLabel }: Case) {
  return (
    <li className="menu-item">
      <NavLink to={`/${urlSlug}`} activeClassName="menu-item-active" exact={true}>
        {menuLabel}
      </NavLink>
    </li>
  )
}
