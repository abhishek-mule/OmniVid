/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export
  output: 'export',
  
  // Base path for production
  basePath: process.env.NODE_ENV === 'production' ? '' : '',
  
  // Asset prefix for static files
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : '',
  
  // Image optimization
  images: {
    unoptimized: true, // Required for static export
  },
  
  // Disable React strict mode for static export
  reactStrictMode: false,
  
  // Configure page extensions
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  
  // Handle trailing slashes
  trailingSlash: true,
  
  // Disable server-side rendering of Link components
  experimental: {
    scrollRestoration: true,
    // Enable server actions if needed
    serverActions: false,
  },
  
  // Environment variables
  env: {
    // Add any client-side environment variables here
    NEXT_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_BASE_URL || '',
  },
}

module.exports = nextConfig