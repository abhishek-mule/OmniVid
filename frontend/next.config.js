/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // optimizeCss: true, // Temporarily disabled to fix build hang
    scrollRestoration: true,
  },
}

module.exports = nextConfig