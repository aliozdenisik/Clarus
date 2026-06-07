import type { Metadata } from "next"

/**
 * Centralized SEO configuration and helpers.
 *
 * The production base URL is read from the environment so deploys can override
 * it without code changes. Set `NEXT_PUBLIC_SITE_URL` in production (it falls
 * back to the legacy `NEXT_PUBLIC_BASE_URL`, then localhost for local dev).
 */

export const locales = ["en", "tr"] as const
export type Locale = (typeof locales)[number]

export const siteConfig = {
  name: "Clarus",
  /** Default production domain — overridable via NEXT_PUBLIC_SITE_URL. */
  defaultUrl: "https://clarus.hollysearch.com",
} as const

/**
 * Resolve the canonical site origin (scheme + host, no trailing slash).
 *
 * Always returns a valid origin so callers like `new URL(getBaseUrl())` cannot
 * throw during metadata initialization. Falls back to the configured default if
 * the environment value is missing or malformed.
 */
export function getBaseUrl(): string {
  const raw =
    process.env.NEXT_PUBLIC_SITE_URL ||
    process.env.NEXT_PUBLIC_BASE_URL ||
    siteConfig.defaultUrl
  try {
    return new URL(raw).origin
  } catch {
    return new URL(siteConfig.defaultUrl).origin
  }
}

/** OpenGraph locale code for a given app locale. */
export function ogLocale(locale: string): string {
  return locale === "tr" ? "tr_TR" : "en_US"
}

/**
 * Build canonical + hreflang alternates for a path that lives under every
 * locale. `path` is the locale-relative path (e.g. "/quran" or "" for home).
 */
export function buildAlternates(locale: string, path = ""): Metadata["alternates"] {
  const base = getBaseUrl()
  const clean = path && !path.startsWith("/") ? `/${path}` : path
  return {
    canonical: `${base}/${locale}${clean}`,
    languages: {
      en: `${base}/en${clean}`,
      tr: `${base}/tr${clean}`,
      "x-default": `${base}/tr${clean}`,
    },
  }
}

/**
 * Produce metadata for a public content page. Uses an absolute title so the
 * root layout's `%s | Clarus` template does not double up the brand name for
 * titles that already include it.
 */
export function buildPageMetadata(args: {
  locale: string
  path: string
  title: string
  description: string
}): Metadata {
  const { locale, path, title, description } = args
  const base = getBaseUrl()
  const url = `${base}/${locale}${path.startsWith("/") ? path : `/${path}`}`

  return {
    title: { absolute: title },
    description,
    alternates: buildAlternates(locale, path),
    openGraph: {
      title,
      description,
      url,
      siteName: siteConfig.name,
      locale: ogLocale(locale),
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
  }
}
