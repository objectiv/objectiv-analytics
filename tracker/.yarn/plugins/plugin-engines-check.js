module.exports = {
  name: `plugin-engines-check`,
  factory: require => {
    const { execSync } = require("child_process");
    const { readFileSync } = require('fs');
    const semver = require('semver');

    // Read `node` and `npm` engines from package.json
    const data = readFileSync('package.json');
    const { engines } = JSON.parse(data.toString());
    const { node, npm } = engines;

    // Retrieve node version
    const nodeVersion = process.version;

    // Retrieve npm version
    const npmVersion = execSync('npm -v').toString();

    return {
      default: {
        hooks: {
          validateProject(project) {
            if (!semver.satisfies(nodeVersion, node)) {
              throw new Error(
                `The current node version ${nodeVersion} does not satisfy the required version ${node}.`,
              );
            }
            if (!semver.satisfies(npmVersion, npm)) {
              throw new Error(
                `The current npm version ${npmVersion} does not satisfy the required version ${npm}.`,
              );
            }
          },
        },
      },
    };
  },
};