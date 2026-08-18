import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "d2qu4js9gdp9gw.cloudfront.net",
      },
    ],
  },
};

export default nextConfig;
