import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    domains: [],
    unoptimized: true, // This can help with image loading issues in development
  },
};

export default nextConfig;
