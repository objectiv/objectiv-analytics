module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**.ts'],
  setupFiles: ['jest-useragent-mock'],
  moduleNameMapper: {
    '@objectiv/schema': '../../../core/schema/src',
    '@objectiv/tracker-core': '../../../core/tracker/src',
  },
};
