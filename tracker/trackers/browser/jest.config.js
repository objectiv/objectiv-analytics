/*
 * Copyright 2021 Objectiv B.V.
 */

module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**/*.ts'],
  moduleNameMapper: {
    '@objectiv/plugin-(.*)': '<rootDir>/../../plugins/$1/src',
    '@objectiv/testing-tools': '<rootDir>../../core/testing-tools/src',
    '@objectiv/tracker-core': '<rootDir>/../../core/tracker/src',
  },
  setupFilesAfterEnv: ['jest-extended/all'],
};
