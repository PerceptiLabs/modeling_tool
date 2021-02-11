module.exports = {
  moduleFileExtensions: [
    'js',
    'jsx',
    'json',
    // tell Jest to handle *.vue files
    'vue'
  ],
  transform: {
    // process *.vue files with vue-jest
    '^.+\\.vue$': 'vue-jest',
    '.+\\.(css|styl|less|sass|scss|jpg|jpeg|png|svg|gif|eot|otf|webp|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$':
    require.resolve('jest-transform-stub'),
    '^.+\\.jsx?$': 'babel-jest'
  },
  transformIgnorePatterns: [
    "<rootDir>/(node_modules)/(?!vis)"
  ],
  testPathIgnorePatterns: [
    "<rootDir>/(build|docs|node_modules)/"
  ],
  // support the same @ -> src alias mapping in source code
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/renderer/$1'
  },
  // serializer for snapshots
  snapshotSerializers: [
    'jest-serializer-vue'
  ],
  testMatch: [
    '**/tests/unit/**/*.spec.[jt]s?(x)',
    '**/__tests__/*.[jt]s?(x)'
  ],
  // https://github.com/facebook/jest/issues/6766
  testURL: 'http://localhost/',
  preset: '@vue/cli-plugin-unit-jest/presets/no-babel'
}