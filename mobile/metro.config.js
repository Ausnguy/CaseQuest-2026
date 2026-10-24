const path = require('path');
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// The dispatch model lives with the web API so the phone and the server run the same code.
config.watchFolders = [path.resolve(__dirname, '../web/lib')];

module.exports = config;
