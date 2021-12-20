module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**/*.{ts,tsx}'],
  moduleNameMapper: {
    '@objectiv/queue-(.*)': '<rootDir>/../../queues/$1/src',
    '@objectiv/testing-tools': '<rootDir>../../core/testing-tools/src',
    '@objectiv/tracker-core': '<rootDir>/../../core/tracker/src',
    '@objectiv/tracker-core-react': '<rootDir>/../../core/react/src',
    '@objectiv/transport-(.*)': '<rootDir>/../../transports/$1/src',
  },
};
