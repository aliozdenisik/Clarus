import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  // Add empty turbopack config to silence Turbopack/webpack conflict warning
  // Next.js 16 uses Turbopack by default, but Sentry SDK adds webpack config internally
  turbopack: {},
  
  // Tree-shake lucide-react imports (Turbopack-compatible)
  // Automatically converts: import { Search } from 'lucide-react'
  // Into direct imports for smaller bundle size
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },
};

export default withSentryConfig(nextConfig, {
  org: process.env.SENTRY_ORG || "your-org-slug",
  project: "clarus-frontend",
  authToken: process.env.SENTRY_AUTH_TOKEN,
  silent: !process.env.CI,
  tunnelRoute: "/monitoring",
  
  sourcemaps: {
    deleteSourcemapsAfterUpload: true,
  },
});
