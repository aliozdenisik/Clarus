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

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = getBaseUrl()
  const lastModified = new Date()

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
