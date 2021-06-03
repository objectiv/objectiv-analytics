export type AbstractContext = {
  _context_type: string;
  id: string;
};

export type AbstractGlobalContext = AbstractContext & {
  _context_kind: 'GlobalContext';
};
export type AbstractLocationContext = AbstractContext & {
  _context_kind: 'LocationContext';
};
