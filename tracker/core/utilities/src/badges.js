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
const path = require('path');

(async () => {
  // Read README.md
  const readmeFileContent = await fs.promises.readFile('README.md', 'utf8');

  // Process license badge
  const licenseBadgeValue = await getLicenseBadgeValue();

  // Process coverage badge
  const coverageBadgeValue = await getCoverageBadgeValue();

  // Update badge values
  updateBadgeValue(readmeFileContent, 'License', licenseBadgeValue);
  updateBadgeValue(readmeFileContent, 'Coverage', coverageBadgeValue);

  console.log(`Processed License badge: ${licenseBadgeValue}`);
  console.log(`Processed Coverage badge: ${coverageBadgeValue}`);
})();

const getCoverageBadgeValue = async () => {
  const coverageReportFileContent = await fs.promises.readFile(path.join('coverage', 'coverage-summary.json'), 'utf8');

  // Parse coverage JSON Summary
  const coverageReportJson = JSON.parse(coverageReportFileContent);

  // Retrieve the total statements percentage
  const coveragePercentage = coverageReportJson.total.statements.pct;

  // Determine badge color - quite arbitrarily
  const badgeColor =
    coveragePercentage >= 90
      ? 'brightgreen'
      : coveragePercentage >= 80
        ? 'yellow'
        : coveragePercentage >= 70
          ? 'orange'
          : 'red';

  // Build shields.io badge URL using `coveragePercentage` and `badgeColor` variables determined above
  return encodeURI(`https://img.shields.io/badge/Coverage-${coveragePercentage}%-${badgeColor}.svg`);
}

const getLicenseBadgeValue = async () => {
  // Read package JSON
  const packageJsonFileContent = await fs.promises.readFile('package.json', 'utf8');

  // Parse package JSON
  const packageJson = JSON.parse(packageJsonFileContent);

  // Retrieve the license
  const license = packageJson.license;

  return encodeURI(`https://img.shields.io/badge/license-${license}-blue.svg?style=flat`);
}

const updateBadgeValue = (readmeFileContent, badgeName, badgeValue) => {
  // const pattern = `![Coverage]`;
  // const enpatterned = (value: string) => `${pattern}(${value})`;
  //
  // const startIndex = newReadmeFile.indexOf(pattern);
  // const valueToChangeStart = newReadmeFile.slice(startIndex + pattern.length);
  //
  // const valueToChangeIndex = valueToChangeStart.indexOf(')');
  // const valueToChangeFinal = valueToChangeStart.substring(1, valueToChangeIndex);
  //
  // const oldBadge = enpatterned(valueToChangeFinal);
  // const newBadge = enpatterned(coverageBadge as string);
  //
  // if (getArgumentValue('ci') && oldBadge !== newBadge) {
  //   reject("The coverage badge has changed, which isn't allowed with the `ci` argument");
  // }
  //
  // newReadmeFile = newReadmeFile.replace(oldBadge, newBadge);


  // Process license badge
  // [license-image]: https://img.shields.io/badge/license-Apache--2-blue.svg?style=flat
  // [license]: https://www.apache.org/licenses/LICENSE-2.0
}