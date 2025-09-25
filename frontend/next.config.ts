import type { NextConfig } from "next";

// Only require bundle analyzer if not in test environment
const withBundleAnalyzer = process.env.NODE_ENV === 'test'
  ? (config: NextConfig) => config
  : require('@next/bundle-analyzer')({
      enabled: process.env.ANALYZE === 'true',
    });

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8004',
        pathname: '/images/**',
      },
      {
        protocol: 'https',
        hostname: 'example.com',
        pathname: '/images/**',
      },
    ],
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  env: {
    NEXT_PUBLIC_AUTH_API_URL: process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://localhost:8001',
    NEXT_PUBLIC_PRODUCTS_API_URL: process.env.NEXT_PUBLIC_PRODUCTS_API_URL || 'http://localhost:8004',
    NEXT_PUBLIC_CART_API_URL: process.env.NEXT_PUBLIC_CART_API_URL || 'http://localhost:8007',
  },
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
  },
  // Simplified webpack config for better build stability
  webpack: (config, { isServer }) => {
    // Only apply optimizations on client-side
    if (!isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          ...config.optimization?.splitChunks,
          cacheGroups: {
            ...config.optimization?.splitChunks?.cacheGroups,
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              priority: 10,
              chunks: 'all',
            },
          },
        },
      };
    }

    return config;
  },
  // Skip static optimization for pages that make API calls
  generateBuildId: async () => {
    return process.env.BUILD_ID || 'build-' + Date.now();
  },
};

export default withBundleAnalyzer(nextConfig);
