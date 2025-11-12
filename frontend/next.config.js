/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // optimizeCss: true, // Temporarily disabled to fix build hang
    scrollRestoration: true,
  },
  // Ensure static files are properly handled
  distDir: '.next',
  // Enable static HTML export
  output: 'standalone',
  // Ensure public directory is included in the build
  images: {
    unoptimized: true, // Disable image optimization if not needed
  },
  // Ensure static files are properly served
  async headers() {
    return [
      {
        source: '/:all*(svg|jpg|png|webp|avif|otf|ttf|woff|woff2|css|js)',
        locale: false,
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig