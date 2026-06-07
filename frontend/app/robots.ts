import type { MetadataRoute } from "next"
import { getBaseUrl } from "@/lib/seo"

/**
 * robots.txt — served at /robots.txt.
 *
 * Allows crawling of public pages while keeping authenticated / utility routes
 * out of the index. Points crawlers at the sitemap.
 */
export default function robots(): MetadataRoute.Robots {
  const baseUrl = getBaseUrl()

  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/api/",
          "/monitoring",
          "/*/hub",
          "/*/compare",
          "/*/search",
          "/*/settings",
          "/*/history",
          "/*/onboarding",
          "/*/sign-in",
          "/*/sign-up",
          "/*/forgot-password",
          "/*/reset-password",
          "/*/email-verification",
          "/*/billing/",
        ],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
    host: baseUrl,
  }
}
