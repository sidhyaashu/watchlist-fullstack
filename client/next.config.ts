import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /**
   * API Rewrites: In development, Next.js proxies /api/* calls to the
   * gateway running on localhost:80, preventing browser CORS issues.
   * In production (Docker), NEXT_PUBLIC_API_URL points to the gateway.
   */
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:80";
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
