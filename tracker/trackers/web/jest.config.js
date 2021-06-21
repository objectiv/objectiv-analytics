module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**.ts'],
  setupFiles: ['jest-useragent-mock'],
  moduleNameMapper: {
    '@objectiv/tracker-core': '../../../core/tracker/src',
    '@objectiv/plugin-(.*)': '../../../plugins/$1/src',
  },
};
