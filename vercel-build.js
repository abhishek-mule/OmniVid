// This script ensures the build runs from the frontend directory
const { execSync } = require('child_process');
const path = require('path');

console.log('Running custom build script...');

process.chdir(path.join(__dirname, 'frontend'));
console.log('Changed to directory:', process.cwd());

console.log('Installing dependencies...');
execSync('npm install', { stdio: 'inherit' });

console.log('Running build...');
execSync('npm run build', { stdio: 'inherit' });

console.log('Build completed successfully!');
