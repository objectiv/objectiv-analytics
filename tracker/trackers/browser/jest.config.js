module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**/*.ts'],
  moduleNameMapper: {
    '@objectiv/tracker-core': '<rootDir>/../../core/tracker/src',
    '@objectiv/plugin-(.*)': '<rootDir>/../../plugins/$1/src',
  },
  setupFilesAfterEnv: ['jest-extended'],
};
