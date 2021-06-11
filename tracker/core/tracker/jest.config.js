module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**.ts'],
  moduleNameMapper: {
    '@objectiv/schema': '../../../core/schema/src',
  },
};
