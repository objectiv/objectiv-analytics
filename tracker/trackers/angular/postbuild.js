const fs = require('fs');

fs.copyFile('.npmrc', './dist/.npmrc', (err) => {
  if (err) throw err;
  console.log('✔ .npmrc  copied to ./dist/.npmrc');
});
