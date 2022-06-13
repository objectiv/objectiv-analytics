/*
 * Copyright 2022 Objectiv B.V.
 */

module.exports = {
  preset: 'react-native',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**/*.{ts,tsx}'],
  moduleNameMapper: {
    '@objectiv/developer-tools': '<rootDir>../../core/developer-tools/src',
    '@objectiv/testing-tools': '<rootDir>../../core/testing-tools/src',
    '@objectiv/tracker-core': '<rootDir>../../core/tracker/src',
    '@objectiv/tracker-react-core': '<rootDir>../../core/react/src',
    '@objectiv/tracker-react-native': '<rootDir>../../trackers/react-native/src',
    '@objectiv/plugin-(.*)': '<rootDir>/../../plugins/$1/src',
    '@objectiv/queue-(.*)': '<rootDir>/../../queues/$1/src',
    '@objectiv/transport-(.*)': '<rootDir>/../../transports/$1/src',
  },
  setupFiles: ['<rootDir>/jest.setup.js'],
  transformIgnorePatterns: [
    'node_modules/(?!(jest-)?react-native|react-clone-referenced-element|@react-native-community|rollbar-react-native|@fortawesome|@react-native|@react-navigation)',
  ],
};
