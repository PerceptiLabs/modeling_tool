const path = require("path");

module.exports = ({ config, mode }) => {
  config.module.rules.push({
    test: /\.scss$/,
    use: [
      require.resolve("vue-style-loader"),
      require.resolve("css-loader"),
      require.resolve("sass-loader"),
    ],
  });

  config.module.rules.push({
    test: /\.(css|scss)$/,
    loaders: [
      {
        loader: "postcss-loader",
        options: {
          sourceMap: true,
          config: {
            path: "./.storybook/",
          },
        },
      },
    ],

    include: path.resolve(__dirname, "../storybook/"),
  });

  return config;
};
