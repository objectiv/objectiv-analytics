# Objectiv Tracker

[![License][license-badge]][license-url]

Objectiv’s Tracker enables you to track user behaviour for web applications, websites and other JavaScript-based applications. It embraces the open taxonomy for analytics to ensure the collected data is clean, well-structured and ready for modeling.

Platform-specific tracker packages are available for popular frameworks such as React and Angular. Trackers can be extended with plugins, which are independent packages that can be configured in any Tracker instance to add or mutate contextual information.

## Installing Objectiv's Tracker

For installation instructions for your preferred platform, please choose a tracker package:

| Name                                            | Type    | Path                          | Links                                                     |
| ----------------------------------------------- | ------- | ----------------------------- | --------------------------------------------------------- |
| @objectiv-analytics/tracker-angular             | tracker | /trackers/angular             | [README](/tracker/trackers/angular/README.md)             |
| @objectiv-analytics/tracker-browser             | tracker | /trackers/browser             | [README](/tracker/trackers/browser/README.md)             |

For detailed installation & usage instructions, visit [Objectiv Docs](https://www.objectiv.io/docs/tracking).

## Support & Troubleshooting
If you need help using or installing Objectiv's tracker, join our [Slack channel](https://join.slack.com/t/objectiv-io/shared_invite/zt-u6xma89w-DLDvOB7pQer5QUs5B_~5pg) and post your question there. 

## Bug Reports & Feature Requests
If you’ve found an issue or have a feature request, please check out the [Contribution Guide](https://www.objectiv.io/docs/the-project/contributing.md).

## Security Disclosure
Found a security issue? Please don’t use the issue tracker but contact us directly. See [SECURITY.md](../SECURITY.md) for details.

## Roadmap
Future plans for Objectiv can be found on our [Github Roadmap](https://github.com/objectiv/objectiv-analytics/projects/2).

## Custom Development & Contributing Code
If you want to contribute to Objectiv or use it as a base for custom development, take a look at [CONTRIBUTING.md](CONTRIBUTING.md). It contains detailed development instructions and a link to information about our contribution process and where you can fit in.

## License
This repository is part of the source code for Objectiv, which is released under the Apache 2.0 License. Please refer to [LICENSE.md](../LICENSE.md) for details.

Unless otherwise noted, all files © 2021 Objectiv B.V.
=======
# Objectiv JavaScript Tracker

Objectiv tracker monorepo.

---
## Overview
The Objectiv JavaScript Tracker is composed of three workspaces. 

- **Core** modules are generic Types, Interfaces and Classes used by Plugins and Trackers.  
  It provides the **JavaScript Tracker Core** and **Schema** modules.


- **Plugins** are independent packages that can be configured in any Tracker instance to add or mutate contextual information.  
  

- **Trackers** are platform specific extensions of the generic **Core** Tracker.  
  They offer a higher level, easier to configure and use, API and may be bundled with a sensible set of **Plugins** for their target environment.

## Packages

This is a complete list of the currently available packages.

| Name                                            | Type    | Path                          | Links                                                     |
| ----------------------------------------------- | ------- | ----------------------------- | --------------------------------------------------------- |
| @objectiv-analytics/schema                      | core    | /core/schema                  | [README](/tracker/core/schema/README.md)                  |
| @objectiv-analytics/tracker-core                | core    | /core/tracker                 | [README](/tracker/core/tracker/README.md)                 |
| @objectiv-analytics/utilities                   | core    | /core/utilities               | [README](/tracker/core/utilities/README.md)               |
| @objectiv-analytics/plugin-web-document-context | plugin  | /plugins/web-document-context | [README](/tracker/plugins/web-document-context/README.md) |
| @objectiv-analytics/tracker-angular             | tracker | /trackers/angular             | [README](/tracker/trackers/angular/README.md)             |
| @objectiv-analytics/tracker-browser             | tracker | /trackers/browser             | [README](/tracker/trackers/browser/README.md)             |

>Note: Packages may be completely independent of each other. Currently, many of them share the same testing framework or bundler but that's not required. Each has its own local configurations and may diverge if needed.

# Monorepo

Objectiv Tracker is a monorepo workspace residing in the `tracker` folder under the `objectiv-analytics` repository.

The monorepo is configured to allow for live development on any package without the need of building anything. This means that both TypeScript and Jest have their module resolutions setup to map to the modules' source files dependencies in package.json.

## Requirements

- git
- Node.js 12
- Yarn

## Workspace commands

While running commands from inside a specific module directory works as expected, it's also possible to execute a command for a specific package from anywhere in the monorepo, without changing directory:

```bash
yarn workspace <package name> <command>
```

For example, this command will run tests only for the Core module:
```bash
yarn workspace @objectiv-analytics/tracker-core test
```

## Dependency management


### Add / Remove dependencies
This is how to add/update or remove dependencies for a specific package:

#### Using `yarn workspace`
```bash
yarn workspace @objectiv-analytics/tracker-core add <packageA>
yarn workspace @objectiv-analytics/tracker-core add <packageB> --dev
yarn workspace @objectiv-analytics/tracker-core remove <packageA> <packageB>
```

#### Using `yarn add`
From inside the directory of one of the packages:

```bash
yarn add <packageA>
yarn add <packageB> --dev
yarn install 
```

> Note: We do not recommend upgrading dependencies per package unless really needed for compatibility reasons.
> 
> It makes much more sense to manage common dependencies via `yarn up`.
> 
> This ensures that sub-packages will not need their own `node_modules` linker and instead rely entirely on the shared 
> one, located in the root of the workspace.
> 
> Fewer dependencies results also in faster builds, and a reduced risk to run into incompatibilities between packages.

### Upgrade dependencies

#### For all packages:

```bash
yarn up <package>
```

#### For all packages, interactively:

```bash
yarn up <package> -i
```

## Building / publishing packages
To locally publish the packages (so they can be used by applications), we use verdaccio. By far, the easiest way, is to run
```bash
make publish
```
from the root of the repo.

To have a little more control, you can also manually run the steps involved:
```bash
## start up verdaccio in Docker container
cd verdaccio && make run

## install requirements
yarn install

## build tracker
yarn build

## publish it
yarn publish:verdaccio
```

Now surf to http://localhost:4873, and you should see the packages you've just published. 

To stop verdaccio, simply run:
```bash
cd verdaccio && make stop
```
Stopping verdaccio will also remove any published packages (as the storage isn't persistent.)
## Other useful commands

The following commands will be executed for all packages automatically when issued from the monorepo root; the `/tracker` directory. 

### `yarn clear`
Deletes all `dist` and `coverage` folders of `core`, `plugins` and `trackers`.
Removes also leftover `.npmrc` from failed publishing to Verdaccio.

### `yarn list`
Prints a list of all the packages configured in the monorepo.

### `yarn install`
Install dependencies for all packages and links local packages to each other.

### `yarn prettify`
Runs prettier for all packages in write mode.

### `yarn prettify:generated`
Runs prettier for `core/schema/src/*`, `core/tracker/src/ContextFactories.ts` and `core/tracker/src/EventFactories.ts` in write mode.

### `yarn tsc`
Runs the TypeScript compiler for all typed packages.

### `yarn test`
Runs the tests for all packages.

### `yarn test:live`
Starts the React Tracker live testing App. This is a playground that executes from sources. Useful for debugging.

### `yarn test:ci`
Runs the tests for all packages in CI mode.

### `yarn test:coverage`
Runs the tests for all packages and collects coverage.
Coverage output will be produced in a `/coverage` folder under each package.

### `yarn build`
Builds all packages.
Build output will be produced in a `/dist` folder under each package.

### `yarn publish`
Publishes all public packages to NPM.
> **Note**:  
> To publish a single package the command name is `npm-publish` to avoid conflicting with the default command 
> 
> Example: `yarn workspace @objectiv-analytics/tracker-core npm-publish`

### `yarn publish:verdaccio`
Publishes all public packages to a Local Verdaccio instance.
> **Note**:  
> To publish a single package the command name is `npm-publish:verdaccio` to avoid conflicting with the default command
>
> Example: `yarn workspace @objectiv-analytics/tracker-core npm-publish:verdaccio`

### `yarn generate:schema`
Runs the generator utility. This will generate:
- The @objectiv-analytics/schema package TypeScript definitions from the OSF
- The Context and Event factories in @objectiv-analytics/tracker-core package from the @objectiv-analytics/schema 

### `yarn generate:badges`
Runs the README badges generator utility. This will update badges placeholders in README.md files.

## Versioning  commands
 - [Release Workflow Documentation](https://yarnpkg.com/features/release-workflow)

### `yarn version --help`
Shows the `version` command help

### `yarn version --interactive`
Creates a release strategy for the current branch

### `yarn version check`
Verifies if there are changes in the current branch and if a release strategy has been created

### `yarn version apply --all`
Executes the release strategy and bumps versions accordingly

## Troubleshooting

#### `Error: Cannot find module '[...]/angular/node_modules/rollup/dist/rollup.js'`
This error can occur when switching between Node.JS versions.   
Delete `tracker/node_modules` and rerun `yarn install` to create a fresh copy. Everything should work fine after that.

## Copyright and license
Licensed and distributed under the Apache 2.0 License (An OSI Approved License).

Copyright (c) 2021 Objectiv B.V.

All rights reserved.
[license-badge]: https://img.shields.io/badge/license-Apache-2.0-blue.svg
[license-url]: https://www.apache.org/licenses/LICENSE-2.0

