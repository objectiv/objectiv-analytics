import { Node, Project } from 'ts-morph';

const TSCONFIG_PATH = 'tsconfig.json';
const SCHEMA_PATH = 'schema/index.ts';

const project = new Project({
  // Load tsconfig to get all the compiler options
  tsConfigFilePath: TSCONFIG_PATH,

  // Skip adding all of our sources; we only want to process the schema path and resolve those files.
  skipAddingFilesFromTsConfig: true,
  skipFileDependencyResolution: true,
  skipLoadingLibFiles: true,
});

// Add source files manually and resolve their dependencies
project.addSourceFilesAtPaths(SCHEMA_PATH);
project.resolveSourceFileDependencies();

// Now we can get the source files to process them up
const sourceFiles = project.getSourceFiles();

// Traverse source files
sourceFiles.forEach((sourceFile) => {

  // For each source file get all the Type aliases
  const typeAliases = sourceFile.getTypeAliases();

  // Go through all Type Aliases
  typeAliases.forEach(typeAlias => {
    console.log(typeAlias.getName());
    console.log(typeAlias.getStructure());

    // Search for properties and their types
    typeAlias.forEachDescendant(typeAliasDescendant => {
      if (Node.isPropertySignature(typeAliasDescendant)) {
        console.log(' -', typeAliasDescendant.getName(), typeAliasDescendant.getType().getText())
      }
    })
  })
});
