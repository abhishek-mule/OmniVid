/** @type {import('next').NextConfig} */
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
};

module.exports = nextConfig;
