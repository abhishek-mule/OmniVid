/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  // Remove 'output: export' for development to enable API routes
  // output: 'export',
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    // Enable image optimization in development
    unoptimized: false,
    domains: ['localhost'],
  },
  // Enable React Strict Mode
  reactStrictMode: true,
  
  // Add webpack configuration to handle the shared package
  webpack: (config, { isServer }) => {
    // Add path aliases for the shared package
    config.resolve.alias['@omnivid/shared'] = path.resolve(__dirname, '../packages/shared');
    return config;
  },
  
  // Enable experimental features if needed
  experimental: {
    externalDir: true,
  },
};

module.exports = nextConfig;
