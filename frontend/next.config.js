/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export
  output: 'export',
  
  // Base path for production (empty for root domain)
  basePath: '',
  
  // Asset prefix for static files
  assetPrefix: '',
  
  // Image optimization
  images: {
    unoptimized: true, // Required for static export
  },
  
  // Disable React strict mode for static export
  reactStrictMode: false,
  
  // Configure page extensions
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  
  // Handle trailing slashes (important for static export)
  trailingSlash: true,
  
  // Environment variables
  env: {
    // Add any client-side environment variables here
    NEXT_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_BASE_URL || '',
  },
  
  // Disable image optimization API routes in static export
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