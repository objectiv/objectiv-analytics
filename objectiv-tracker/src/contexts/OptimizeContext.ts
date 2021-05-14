export const OPTIMIZE_CONTEXT_TYPE = 'OptimizeContext';

export type OptimizeContext = {
  _context_type: typeof OPTIMIZE_CONTEXT_TYPE;
  id: string;
  variant: string;
};

export function createOptimizeContext({ experimentId, variant, ...rest }: { experimentId: string, variant: string }): OptimizeContext {
  return {
    _context_type: OPTIMIZE_CONTEXT_TYPE,
    id: experimentId,
    variant: variant,
    ...rest,
  };
}
