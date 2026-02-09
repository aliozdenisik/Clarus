import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  // Add empty turbopack config to silence Turbopack/webpack conflict warning
  // Next.js 16 uses Turbopack by default, but Sentry SDK adds webpack config internally
  turbopack: {},
  
  // Tree-shake lucide-react barrel imports at build time
  // Transforms: import { Search } from 'lucide-react' → direct icon imports
  modularizeImports: {
    'lucide-react': {
      transform: 'lucide-react/dist/esm/icons/{{kebabCase member}}',
    },
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
