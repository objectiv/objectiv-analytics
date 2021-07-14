const CracoAlias = require('craco-alias');

module.exports = {
  plugins: [
    {
      plugin: CracoAlias,
      options: {
        source: 'tsconfig',
        tsConfigPath: 'tsconfig.extend.json',
      },
    }
  ],
  webpack: {
    configure: {
      module: {
        rules: [
          {
            test: /\.tsx$/,
            use: 'webpack-import-glob-loader'
          },
        ]
      },
    }  }
};
