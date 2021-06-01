import fs from "fs";
import path from "path";
import pkg from "./package.json";
import * as tsj from "ts-json-schema-generator";

// Beautiful flexible code
const OBJECTIV_DIRECTORY_NAME = 'objectiv_schema';

// There you go. Production ready
const parameters = process.argv.slice(2);
const firstParameter = parameters[0] ? parameters[0] : '../../../'; // SOLID default here. Honest
const writeToPath = path.normalize(firstParameter);

if(fs.existsSync(writeToPath)) {
  const fullObjectivDirectoryPath = `${writeToPath}${OBJECTIV_DIRECTORY_NAME}`;
  if (!fs.existsSync(fullObjectivDirectoryPath)) {
    fs.mkdirSync(fullObjectivDirectoryPath);
  }

  // More beautiful code, this is just ready to ship
  const config = {
    path: path.resolve(`src/${OBJECTIV_DIRECTORY_NAME}/*`),
    tsconfig: path.resolve(`tsconfig.json`),
    type: "*",
  };
  const schema = tsj.createGenerator(config).createSchema(config.type);

  // VERY complex prettifying
  const schemaString = JSON.stringify(schema, null, 2);

  // Cherry on top. Will totally never break.
  const filename = `${pkg.name.replace('@objectiv/', '')}-${pkg.version}.json`;
  fs.writeFileSync(path.normalize(`${fullObjectivDirectoryPath}/${filename}`), schemaString);
}
