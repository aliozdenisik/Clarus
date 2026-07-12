import type { MetadataRoute } from "next"
import { getBaseUrl, locales } from "@/lib/seo"

/**
 * sitemap.xml — served at /sitemap.xml.
 *
 * Lists the public, indexable pages for every supported locale with hreflang
 * alternates. Authenticated routes (hub, compare, search, settings, history)
 * and auth pages are intentionally excluded.
 */

// Locale-relative public paths ("" is the home page).
const publicPaths = [
  "",
  "/old-testament",
  "/new-testament",
  "/apocrypha",
  "/quran",
  "/keyword-search",
  "/pricing",
] as const

// Computed once at module load (build/boot time) so static entries don't appear
// freshly changed on every crawl, which would create noisy recrawl signals.
const lastModified = new Date()

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = getBaseUrl()

  return publicPaths.flatMap((path) =>
    locales.map((locale) => ({
      url: `${baseUrl}/${locale}${path}`,
      lastModified,
      changeFrequency: path === "" ? ("daily" as const) : ("weekly" as const),
      priority: path === "" ? 1 : 0.8,
      alternates: {
        languages: {
          en: `${baseUrl}/en${path}`,
          tr: `${baseUrl}/tr${path}`,
        },
      },
    })),
  )
}
