import { Node, Project } from 'ts-morph';

const SCHEMA_PATH = 'schema/index.ts';

const project = new Project();

// Add source files manually and resolve their dependencies
project.addSourceFilesAtPaths(SCHEMA_PATH);
project.resolveSourceFileDependencies();

// Now we can get the source files to process them up
const sourceFiles = project.getSourceFiles();

// Initialize the OSF Schema JSON Object
const schemaJSON: { contexts: { [k: string]: unknown }} = {contexts: {} };

// Traverse source files
sourceFiles.forEach((sourceFile) => {
  // For each source file get all the Type aliases
  const typeAliases = sourceFile.getTypeAliases();

  // Go through all Type Aliases
  typeAliases.forEach((typeAlias) => {
    const typeName = typeAlias.getName();

    // Initialize this new type in schemaJSONString
    const newType: { parents?: string[], properties?: {[k: string]: unknown} } = {};

    // Search for references and properties
    typeAlias.forEachDescendant((typeAliasDescendant) => {
      if (Node.isTypeReferenceNode(typeAliasDescendant)) {
        if (!newType?.parents) {
          newType['parents'] = [];
        }
        newType.parents.push(typeAliasDescendant.getTypeName().getText()); // TODO this type inferring sucks
      }

      if (Node.isPropertySignature(typeAliasDescendant)) {
        const propertyName = typeAliasDescendant.getName();

        // Skip properties starting with `_`. We use these for internal purposes
        if (propertyName.startsWith('_')) {
          return;
        }

        const propertyType = typeAliasDescendant.getType();

        // Add the property to the new type
        if (!newType?.properties) {
          newType['properties'] = {};
        }
        newType.properties[propertyName] = propertyType.isLiteral() ? propertyType.getLiteralValue() : propertyType.getText();
      }
    });

    // Add this type to the schemaJSONString
    schemaJSON.contexts[typeName] = newType;
  });
});

// Output schema
console.log(JSON.stringify(schemaJSON, null, 2));
