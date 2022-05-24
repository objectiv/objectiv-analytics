/*
 * Copyright 2021-2022 Objectiv B.V.
 */

module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**/*.{ts,tsx}'],
  moduleNameMapper: {
    '@objectiv/schema': '<rootDir>../../core/schema/src',
    '@objectiv/tracker-core': '<rootDir>../../core/tracker/src',
    '@objectiv/developer-tools': '<rootDir>../../core/developer-tools/src',
    '@objectiv/testing-tools': '<rootDir>../../core/testing-tools/src',
  },
};
