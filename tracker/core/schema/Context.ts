export type AbstractContext = {
  _context_type: string;
  id: string;
};

export type AbstractGlobalContext = AbstractContext;
export type AbstractLocationContext = AbstractContext & {
  _context_kind: 'LocationContext';
};
