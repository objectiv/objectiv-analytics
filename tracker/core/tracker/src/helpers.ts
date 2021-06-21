/**
 * Generic decorator to extend Interfaces and ensure they will have a class constructor
 */
export type Newable<T> = { new (...args: Record<string, unknown>[]): T };

/**
 * A more flexible implementation of Partial that allows to specify which properties should be Partial
 */
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/**
 * A TypeScript friendly Object.keys
 */
export const getObjectKeys = Object.keys as <T extends object>(obj: T) => Array<keyof T>;
