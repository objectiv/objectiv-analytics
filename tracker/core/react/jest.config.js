module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**/*.{ts,tsx}'],
  moduleNameMapper: {
    '@objectiv/schema': '<rootDir>/../../core/schema/src',
    '@objectiv/tracker-core': '<rootDir>/../../core/tracker/src',
  },
};
