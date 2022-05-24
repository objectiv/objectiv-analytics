# Objectiv Tracker - Development

Here you'll find instructions for development on the Objectiv Tracker. If you want to contribute (Thank you!), please take a look at the [Contribution Guide](https://www.objectiv.io/docs/home/the-project/contribute) in our Docs. It contains information about our contribution process and where you can fit in.

## Overview
The Objectiv JavaScript Tracker is composed of three workspaces. 

- **Core** modules are generic Types, Interfaces and Classes used by Plugins and Trackers.  
  It provides the **JavaScript Tracker Core** and **Schema** modules.


- **Plugins** are independent packages that can be configured in any Tracker instance to add or mutate contextual information.  
  

- **Trackers** are platform specific extensions of the generic **Core** Tracker.  
  They offer a higher level, easier to configure and use, API and may be bundled with a sensible set of **Plugins** for their target environment.

## Packages

This is a complete list of the currently available packages.

| Name                                             | Type      | Path                                     | Links                                                                |
|--------------------------------------------------|-----------|------------------------------------------|----------------------------------------------------------------------|
| @objectiv/developer-tools                        | core      | /core/developer-tools                    | [README](/tracker/core/developer-tools/README.md)                    |
| @objectiv/schema                                 | core      | /core/schema                             | [README](/tracker/core/schema/README.md)                             |
| @objectiv/tracker-core                           | core      | /core/tracker                            | [README](/tracker/core/tracker/README.md)                            |
| @objectiv/tracker-react-core                     | core      | /core/react                              | [README](/tracker/core/react/README.md)                              |
| @objectiv/testing-tools                          | core      | /core/testing-tools                      | [README](/tracker/core/testing-tools/README.md)                      |
| @objectiv/utilities                              | core      | /core/utilities                          | [README](/tracker/core/utilities/README.md)                          |
| @objectiv/http-context                           | plugin    | /plugins/http-context                    | [README](/tracker/plugins/http-context/README.md)                    | 
| @objectiv/plugin-path-context-from-url           | plugin    | /plugins/path-context-from-url           | [README](/tracker/plugins/path-context-from-url/README.md)           |
| @objectiv/plugin-react-navigation                | plugin    | /plugins/react-navigation                | [README](/tracker/plugins/react-navigation/README.md)                |
| @objectiv/plugin-react-router-tracked-components | plugin    | /plugins/react-router-tracked-components | [README](/tracker/plugins/react-router-tracked-components/README.md) |
| @objectiv/plugin-root-location-context-from-url  | plugin    | /plugins/root-location-context-from-url  | [README](/tracker/plugins/root-location-context-from-url/README.md)  |
| @objectiv/tracker-angular                        | tracker   | /trackers/angular                        | [README](/tracker/trackers/angular/README.md)                        |
| @objectiv/tracker-browser                        | tracker   | /trackers/browser                        | [README](/tracker/trackers/browser/README.md)                        |
| @objectiv/tracker-react                          | tracker   | /trackers/react                          | [README](/tracker/trackers/react/README.md)                          |
| @objectiv/tracker-react-native                   | tracker   | /trackers/react-native                   | [README](/tracker/trackers/react-native/README.md)                   |
| @objectiv/transport-debug                        | transport | /transports/browser                      | [README](/tracker/transports/debug/README.md)                        |
| @objectiv/transport-fetch                        | transport | /transports/browser                      | [README](/tracker/transports/fetch/README.md)                        |
| @objectiv/transport-xhr                          | transport | /transports/browser                      | [README](/tracker/transports/xhr/README.md)                          |

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
yarn workspace @objectiv/tracker-core test
```

## Dependency management


### Add / Remove dependencies
This is how to add/update or remove dependencies for a specific package:

#### Using `yarn workspace`
```bash
yarn workspace @objectiv/tracker-core add <packageA>
yarn workspace @objectiv/tracker-core add <packageB> --dev
yarn workspace @objectiv/tracker-core remove <packageA> <packageB>
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
Runs prettier for `core/schema/src/*`, `core/tracker/src/ContextFactories.ts`, `core/tracker/src/ContextNames.ts` and `core/tracker/src/EventFactories.ts` in write mode.

### `yarn tsc`
Runs the TypeScript compiler for all typed packages.

### `yarn tsc:generated`
Runs the TypeScript compiler for `core/schema` and `core/tracker`.

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

### `TAG=<latest|next> yarn publish`
Publishes all public packages to NPM.
> **Note**:  
> To publish a single package the command name is `npm-publish` to avoid conflicting with the default command 
> 
> Example: `TAG=next yarn workspace @objectiv/tracker-core npm-publish`

### `TAG=<latest|next> yarn publish:verdaccio`
Publishes all public packages to a Local Verdaccio instance.
> **Note**:  
> To publish a single package the command name is `npm-publish:verdaccio` to avoid conflicting with the default command
>
> Example: `TAG=next yarn workspace @objectiv/tracker-core npm-publish:verdaccio`

### `yarn utils:generate`
Runs the generator utility. This will generate:
- The @objectiv/schema package TypeScript definitions from the OSF
- The Context and Event factories in @objectiv/tracker-core package from the @objectiv/schema 
- The ContextErrorMessages in @objectiv/developer-tools package 
- Yarn prettify for all generated files
- TypeScript for all generated files

## Versioning  commands
 - [Release Workflow Documentation](https://yarnpkg.com/features/release-workflow)

### `yarn version --help`
Shows the `version` command help

### `yarn version check --interactive`
Creates a release strategy for the current branch

### `yarn version check`
Verifies if there are changes in the current branch and if a release strategy has been created

### `yarn version apply --all`
Executes the release strategy and bumps versions accordingly

### `yarn version:patch`
Patches all packages right away, without using version release strategies

### `yarn version:minor`
Bumps the minor of all packages right away, without using version release strategies

### `yarn version:major`
Bumps the major of all packages right away, without using version release strategies

### `yarn version:prerelease`
Patches all packages and either adds or increment the prerelease postfix right away, without using version release strategies

## Troubleshooting

#### `Error: Cannot find module '[...]/angular/node_modules/rollup/dist/rollup.js'`
This error can occur when switching between Node.JS versions.   
Delete `tracker/node_modules` and rerun `yarn install` to create a fresh copy. Everything should work fine after that.
