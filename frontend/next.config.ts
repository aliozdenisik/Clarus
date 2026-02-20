import type { NextConfig } from "next"
import { withSentryConfig } from "@sentry/nextjs"
import createNextIntlPlugin from "next-intl/plugin"

const withNextIntl = createNextIntlPlugin("./i18n/request.ts")

const nextConfig: NextConfig = {
  // Add empty turbopack config to silence Turbopack/webpack conflict warning
  // Next.js 16 uses Turbopack by default, but Sentry SDK adds webpack config internally
  turbopack: {},

  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "www.shadcnblocks.com",
        pathname: "/images/**",
      },
      {
        protocol: "https",
        hostname: "images.unsplash.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "svgl.app",
        pathname: "/library/**",
      },
      {
        protocol: "https",
        hostname: "i.pravatar.cc",
        pathname: "/**",
      },
    ],
  },

  // Tree-shake lucide-react and recharts imports (Turbopack-compatible)
  // Automatically converts named imports into direct subpath imports for smaller bundle size
  // recharts: ensures only used chart components (BarChart, Bar, XAxis, etc.) are bundled (#248)
  experimental: {
    optimizePackageImports: ["lucide-react", "recharts"],
  },
}

export default withSentryConfig(withNextIntl(nextConfig), {
  org: process.env.SENTRY_ORG || "your-org-slug",
  project: "clarus-frontend",
  authToken: process.env.SENTRY_AUTH_TOKEN,
  silent: !process.env.CI,
  tunnelRoute: "/monitoring",

  sourcemaps: {
    deleteSourcemapsAfterUpload: true,
  },

  // Reduce Sentry client bundle size (#249)
  disableLogger: true,
  bundleSizeOptimizations: {
    excludeDebugStatements: true,
    excludeReplayCanvas: true,
    excludeReplayIframe: true,
    excludeReplayShadowDom: true,
    excludeReplayWorker: true,
  },
})
