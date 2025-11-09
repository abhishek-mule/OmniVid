/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  compiler: {
    styledComponents: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  experimental: {
    // Add any experimental features here
  },
  webpack: (config) => {
    // Add any webpack configurations here
    return config;
  },
}

module.exports = nextConfig
