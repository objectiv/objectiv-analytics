import fs from 'fs';
import { Node, Project } from 'ts-morph';

const SCHEMA_PATH = 'schema/index.ts';
const DESTINATION_PATH = '../../schema';
const DESTINATION_JSON_NAME = 'base.json';

const project = new Project();

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
    const newType: { [k: string]: unknown, parents: string[] } = {
      parents: []
    };

    // Search for references and properties
    typeAlias.forEachDescendant((typeAliasDescendant) => {
      if (Node.isTypeReferenceNode(typeAliasDescendant)) {
        newType.parents.push(typeAliasDescendant.getTypeName().getText()); // TODO this type inferring sucks
      }

      if (Node.isPropertySignature(typeAliasDescendant)) {
        const propertyName = typeAliasDescendant.getName();

        // Skip properties starting with `_`. We use these for internal purposes
        if (propertyName.startsWith('_')) {
          return;
        }

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
