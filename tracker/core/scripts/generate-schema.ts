import fs from 'fs';
import { Node, Project } from 'ts-morph';

const TSCONFIG_PATH = 'tsconfig.json';
const SCHEMA_PATH = 'schema/index.ts';
const DESTINATION_PATH = '../../schema';
const DESTINATION_JSON_NAME = 'base.json';

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

// Initialize the OSF Schema JSON Object
const schemaJSON: { [k: string]: unknown } = {};

// Traverse source files
sourceFiles.forEach((sourceFile) => {
  // For each source file get all the Type aliases
  const typeAliases = sourceFile.getTypeAliases();

  // Go through all Type Aliases
  typeAliases.forEach((typeAlias) => {
    const typeName = typeAlias.getName();

    // Initialize this new type in schemaJSONString
    const newType: { [k: string]: unknown } = {};

    // Search for references and properties
    typeAlias.forEachDescendant((typeAliasDescendant) => {
      if (Node.isTypeReferenceNode(typeAliasDescendant)) {
        // TODO check if this is correct
        newType['parent'] = typeAliasDescendant.getTypeName().getText(); // TODO this sucks
      }

      if (Node.isPropertySignature(typeAliasDescendant)) {
        const propertyName = typeAliasDescendant.getName();

        // Add the property to the new type
        const propertyType = typeAliasDescendant.getType();
        newType[propertyName] = propertyType.isLiteral() ? propertyType.getLiteralValue() : propertyType.getText();
      }
    });

    // Add this type to the schemaJSONString
    schemaJSON[typeName] = newType;
  });
});

// Create schema destination dir if it doesn't exist
if (!fs.existsSync(DESTINATION_PATH)) {
  fs.mkdirSync(DESTINATION_PATH);
}

// Write base schema
const schemaJSONString = JSON.stringify(schemaJSON, null, 2);
console.log(schemaJSONString);
fs.writeFileSync(`${DESTINATION_PATH}/${DESTINATION_JSON_NAME}`, schemaJSONString);
