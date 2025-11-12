/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export
  output: 'export',
  // Set base path if your app is not served from the root
  basePath: process.env.NODE_ENV === 'production' ? '' : '',
  // Enable image optimization
  images: {
    unoptimized: true, // Required for static export
  },
  // Disable React strict mode for static export
  reactStrictMode: false,
  // Add asset prefix for static export
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : '',
  // Configure page extensions
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  // Handle trailing slashes
  trailingSlash: true,
}

module.exports = nextConfig