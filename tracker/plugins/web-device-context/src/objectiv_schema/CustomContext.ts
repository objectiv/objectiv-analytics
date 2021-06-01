import { GlobalContext } from "@objectiv/core";
import { Balls } from "./CustomTypes";

export type CustomContext = GlobalContext & {
  _context_type: 'CustomContext';
  meta: {
    whatever: string,
    amaze: Balls
  }
}
