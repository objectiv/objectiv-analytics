/*
 * Copyright 2022 Objectiv B.V.
 */

module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**/*.ts'],
  moduleNameMapper: {
    '@objectiv/developer-tools': '<rootDir>../../core/developer-tools/src',
    '@objectiv/testing-tools': '<rootDir>../../core/testing-tools/src',
    '@objectiv/tracker-core': '<rootDir>../../core/tracker/src',
    '@objectiv/plugin-(.*)': '<rootDir>/../../plugins/$1/src',
  },
  setupFilesAfterEnv: ['jest-extended/all'],
};
