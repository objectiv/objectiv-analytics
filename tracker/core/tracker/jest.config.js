/*
 * Copyright 2021 Objectiv B.V.
 */

module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  reporters: ['jest-standard-reporter'],
  coverageReporters: ['lcov', 'text', 'json-summary'],
  collectCoverageFrom: ['src/**.ts'],
  moduleNameMapper: {
    '@objectiv-analytics/schema': '<rootDir>../../core/schema/src',
  },
};
