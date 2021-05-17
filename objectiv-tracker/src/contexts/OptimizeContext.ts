export const OPTIMIZE_CONTEXT_TYPE = 'OptimizeContext';

export type OptimizeContext = {
  _context_type: typeof OPTIMIZE_CONTEXT_TYPE;
  id: string;
  variant: string;
  propertyId: string;
};

export function createOptimizeContext({ experimentId, variant, propertyId, ...rest }: {
    experimentId: string, variant: string, propertyId: string }): OptimizeContext {
  return {
    _context_type: OPTIMIZE_CONTEXT_TYPE,
    id: experimentId,
    variant: variant,
    propertyId: propertyId,
    ...rest,
  };
}
