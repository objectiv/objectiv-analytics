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

  // For each source file get all children
  sourceFile.forEachChild((node) => {

    // We only care about TypeAlias Declarations
    if (Node.isTypeAliasDeclaration(node)) {

      // The symbol will allow us to get the type name
      const typeSymbol = node.getSymbol();
      const typeName = typeSymbol?.getName();
      console.log(typeName);

      // Search for properties
      node.forEachDescendant(typeLiteralDescendant => {
        if (Node.isPropertySignature(typeLiteralDescendant)) {
          const propertySymbol = typeLiteralDescendant.getSymbol();
          const propertyName = propertySymbol?.getName();

          console.log(' -', propertyName, typeLiteralDescendant.getType().getText())
        }
      })
    }
  })
});