import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  allowedDevOrigins: ["*.trycloudflare.com"],
  reactStrictMode: true,
  devIndicators: false,
  
};

export default nextConfig;
