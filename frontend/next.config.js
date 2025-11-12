/** @type {import('next').NextConfig} */
const nextConfig = {
  // Base path for production (empty for root domain)
  basePath: '',

  // Asset prefix for static files
  assetPrefix: '',

  // Image optimization
  images: {
    // Optimized images for server rendering
  },

  // Enable React strict mode
  reactStrictMode: true,

  // Configure page extensions
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],

  // Handle trailing slashes
  trailingSlash: false,
  
  // Environment variables
  env: {
    // Add any client-side environment variables here
    NEXT_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_BASE_URL || '',
  },
  
  // Disable fs fallback on client side
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
}

module.exports = nextConfig