module.exports = {
  name: `plugin-engines-check`,
  factory: require => {
    const child_process = require("child_process");
    const fs = require('fs');
    const path = require("path");
    const semver = require('semver');

    function getRootPath() {
        return (function getRoot(dir) {
            try {
                const isMonorepoRoot = fs.accessSync(path.join(dir, '.yarn'));
            }
            catch (e) {
              if (dir === '/') {
                // This should never happen, just for sanity
                throw new Error('Could not find monorepo root');
              }
              return getRoot(path.join(dir, '..'));
            }
            return dir;
        }(path.join(__dirname, '../..')));
    }

    // Read `node` and `npm` engines from package.json
    const data = fs.readFileSync(getRootPath() + '/package.json');
    const { engines } = JSON.parse(data.toString());
    const { node, npm } = engines;

    // Retrieve node version
    const nodeVersion = process.version;

    // Retrieve npm version
    const npmVersion = child_process.execSync('npm -v').toString().trim();

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