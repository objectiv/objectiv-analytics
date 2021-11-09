/*
 * Copyright 2021 Objectiv B.V.
 */

/**
 * Generates and updates README badges. Jest json-summary coverage reports for now, and possibly others in the future.
 * The script will automatically update badge placeholders in the README.md of the target workspace, if any.
 *
 * 1. Enable `json-summary` coverage reporter either in jest.config.json or package.json of the target workspace:
 *
 *    in jest.config.json
 *
 *      coverageReporters: ['lcov', 'text', 'json-summary'],
 *
 *    or in package.json
 *
 *      "jest": {
 *        "coverageReporters": [
 *          "lcov",
 *          "text",
 *          "json-summary"
 *        ]
 *      }
 *
 * 2. Add this script to the `scripts` section of the package.json of the target workspace, like so:
 *
 *    scripts: {
 *      "generate:badges": "node ../path/to/core/utilities/src/badges.js",
 *    }
 *
 * 3. Generate coverage reports and then run it to update badges in the readme:
 *
 *    yarn test:coverage
 *    yarn generate:badges
 *
 */

const fs = require('fs');

fs.readFile('./coverage/coverage-summary.json', 'utf8', (error, resource) => {
  if (error) {
    throw error;
  }

  // Parse coverage JSON Summary
  const coverageReportJsonSummary = JSON.parse(resource);

  // Retrieve the total statements percentage
  const coveragePercentage = coverageReportJsonSummary.total.statements.pct;

  // Determine badge color - quite arbitrarily
  const badgeColor =
    coveragePercentage >= 90
      ? 'brightgreen'
      : coveragePercentage >= 80
      ? 'yellow'
      : coveragePercentage >= 70
      ? 'orange'
      : 'red';

  // Build shields.io badge URL using coverPercentage and badgeColor determine above
  const badgeURL = encodeURI(`https://img.shields.io/badge/Coverage-${coveragePercentage}%-${badgeColor}.svg`);

  console.log(`Generated coverage badge: ${badgeURL}`)
});
