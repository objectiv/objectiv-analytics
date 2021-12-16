module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**/*.{ts,tsx}'],
  moduleNameMapper: {
    '@objectiv/tracker-core': '<rootDir>/../../core/tracker/src',
    '@objectiv/tracker-core-react': '<rootDir>/../../core/react/src',
  },
};
