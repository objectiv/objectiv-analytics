# Objectiv JavaScript Tracker
[PLACEHOLDER: Objectiv Tracker introductory text]

---
# Overview
The Objectiv JavaScript Tracker is composed of three workspaces. 

- **Core** modules are generic Types, Interfaces and Classes used by Plugins and Trackers.  
  It provides the **JavaScript Tracker Core** and **Schema** modules.


- **Plugins** are independent packages that can be configured in any Tracker instance to add or mutate contextual information.  
  

- **Trackers** are platform specific extensions of the generic **Core** Tracker.  
  They offer a higher level, easier to configure and use, API and may be bundled with a sensible set of **Plugins** for their target environment.

## Packages

This is a complete list of the currently available packages.

| Name                                  | Type    | Path                          | Links                                                     |
| ------------------------------------- | ------- | ----------------------------- | --------------------------------------------------------- |
| @objectiv/schema                      | core    | /core/schema                  | [README](/tracker/core/schema/README.md)                         |
| @objectiv/tracker-core                | core    | /core/tracker                 | [README](/tracker/core/tracker/README.md)                         |
| @objectiv/plugin-web-device-context   | plugin  | /plugins/web-device-context   | [README](/tracker/plugins/web-device-context/README.md)   |
| @objectiv/plugin-web-document-context | plugin  | /plugins/web-document-context | [README](/tracker/plugins/web-document-context/README.md) |
| @objectiv/tracker-web                 | tracker | /trackers/web                 | [README](/tracker/trackers/web/README.md)                 |

>Note: Packages may be completely independent of each other. Currently, many of them share the same testing framework or bundler but that's not required. Each has its own local configurations and may diverge if needed.

# Monorepo

Objectiv Tracker is a monorepo workspace residing in the `tracker` folder under the `objectiv-analytics` repository.

The monorepo is configured to allow for live development on any package without the need of building anything. This means that both TypeScript and Jest have their module resolutions setup to map to the modules' source files dependencies in package.json.

## Requirements

- git
- Node.js 10
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
make publish-tracker
```
from the root of the repo.

To have a little more control, you can also manually run the steps involved:
```bash
## start up verdaccio in Docker container
cd verdaccio && make run

## build tracker
yarn build

## publish it
yarn publish
```

Now surf to http://localhost:4873 and you should see the packages you've just published. 


## Other useful commands

The following commands will be executed for all packages automatically when issued from the monorepo root; the `/tracker` directory. 

### `yarn list`
Prints a list of all the packages configured in the monorepo.

### `yarn install`
Install dependencies for all packages and links local packages to each other.

### `yarn prettier`
Runs prettier for all packages in write mode.

### `yarn lint`
Lints all packages.

### `yarn test`
Runs the tests for all packages.

### `yarn test:coverage`
Runs the tests for all packages and collects coverage.
Coverage output will be produced in a `/coverage` folder under each package.

### `yarn build`
Builds all packages.
Build output will be produced in a `/dist` folder under each package.
