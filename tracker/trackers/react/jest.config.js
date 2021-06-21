module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**.{ts,tsx}'],
  setupFiles: ['jest-useragent-mock'],
  moduleNameMapper: {
    '@objectiv/core': '../../../core/src',
    '@objectiv/plugin-(.*)': '../../../plugins/$1/src',
    '@objectiv/tracker-core': '../../../core/tracker/src',
    '@objectiv/tracker-web': '../../../trackers/web/src',
  },
};
