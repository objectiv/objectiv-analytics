/*
 * Copyright 2021 Objectiv B.V.
 */

module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  reporters: ['jest-standard-reporter'],
  coverageReporters: ['lcov', 'text', 'json-summary'],
  collectCoverageFrom: ['src/**/*.ts'],
  moduleNameMapper: {
    '@objectiv-analytics/tracker-core': '<rootDir>/../../core/tracker/src',
    '@objectiv-analytics/plugin-(.*)': '<rootDir>/../../plugins/$1/src',
  },
  setupFilesAfterEnv: ['jest-extended/all'],
};
