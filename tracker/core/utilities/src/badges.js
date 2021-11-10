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
 * 3. Add badge placeholders to the README.md
 *    [![License][license-badge]][license-url]
 *    [![Coverage][coverage-badge]]
 *
 * 4. Generate coverage reports and then run it to update badges in the readme:
 *
 *    yarn test:coverage
 *    yarn generate:badges
 *
 */

const fs = require('fs');
const got = require("got");
const path = require('path');

(async () => {
  // Read README.md
  const readmeFileContent = await fs.promises.readFile('README.md', 'utf8');
  let newReadmeFileContent = readmeFileContent;

  // Determine which badges we need to update
  const readmeHasLicenseBadge = readmeFileContent.indexOf('[![License][license-badge]][license-url]') >= 0;
  const readmeHasCoverageBadge = readmeFileContent.indexOf('[![Coverage][coverage-badge]]') >= 0;

  // Process and update License badge
  if (readmeHasLicenseBadge) {
    // Retrieve license badge value and url
    const [licenseBadgeValue, licenseBadgeUrl] = await getLicenseData();

    // Update badge value and url
    newReadmeFileContent = updateBadge(newReadmeFileContent, 'License', licenseBadgeValue, licenseBadgeUrl);

    console.log(`Processed License badge: ${licenseBadgeValue}, ${licenseBadgeUrl}`);
  }

  // Process and update Coverage badge
  if (readmeHasCoverageBadge) {
    // Retrieve coverage badge value
    const coverageBadgeValue = await getCoverageData();

    // Update badge value
    newReadmeFileContent = updateBadge(newReadmeFileContent, 'Coverage', coverageBadgeValue);
    console.log(`Processed Coverage badge: ${coverageBadgeValue}`);
  }

  if (newReadmeFileContent !== readmeFileContent) {
    fs.writeFileSync('README.md', newReadmeFileContent);
    console.log('README.md updated');
  }
})();

const getCoverageData = async () => {
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

const getLicenseData = async () => {
  // Read package JSON
  const packageJsonFileContent = await fs.promises.readFile('package.json', 'utf8');

  // Parse package JSON
  const packageJson = JSON.parse(packageJsonFileContent);

  // Retrieve the license Id
  const licenseId = packageJson.license;

  // Retrieve and parse the license JSON from SPDX
  const licenseJson = await got(`https://spdx.org/licenses/${licenseId}.json`).json();

  // Retrieve the license Url, just pick the first seeAlso item
  const licenseUrl = licenseJson["seeAlso"][0];

  return [
    encodeURI(`https://img.shields.io/badge/license-${licenseId.replace('-', '--')}-blue.svg`),
    licenseUrl
  ];
}

const updateBadge = (readmeFileContent, badgeName, badgeValue, badgeUrl) => {
  let newReadmeFileContent = readmeFileContent;

  if(badgeValue) {
    const badgeKey = `${badgeName.toLowerCase()}-badge`;
    newReadmeFileContent = appendOrReplaceBadgeValue(newReadmeFileContent, badgeKey, badgeValue);
  }

  if(badgeUrl) {
    const badgeKey = `${badgeName.toLowerCase()}-url`;
    newReadmeFileContent = appendOrReplaceBadgeValue(newReadmeFileContent, badgeKey, badgeUrl);
  }

  return newReadmeFileContent;
}

const appendOrReplaceBadgeValue = (readmeFileContent, badgeKey, badgeValue) => {
  // Make new badge value
  const newBadgeValue = `[${badgeKey}]: ${badgeValue}\n`

  // Replace old badge value with the new one or simply append the value if it was not there
  const badgeValueRegex = new RegExp(`\\[${badgeKey}]: .*\\n`);
  if(readmeFileContent.match(badgeValueRegex)) {
    readmeFileContent.replace(badgeValueRegex, newBadgeValue);
  } else {
    readmeFileContent += newBadgeValue;
  }

  return readmeFileContent;
}
