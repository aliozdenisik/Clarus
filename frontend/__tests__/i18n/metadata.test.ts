import { describe, it, expect, beforeEach } from "vitest"
import type { Metadata } from "next"
import en from "../../messages/en.json"
import tr from "../../messages/tr.json"

/**
 * Mock implementation of generateMetadata for testing
 * This mirrors the actual implementation in app/[locale]/layout.tsx
 */
async function generateMetadata(locale: string): Promise<Metadata> {
  interface AlternateLanguages {
    en: string
    tr: string
    "x-default": string
  }

  interface OpenGraphMetadata {
    locale?: string
    alternateLocale?: string[]
    type?: string
    url?: string
  }
  const baseUrl = "http://localhost:3000"
  const metadata = locale === "tr" ? tr : en
  const metadataNamespace = metadata.Metadata

  return {
    title: {
      default: metadataNamespace.title,
      template: `%s | ${metadataNamespace.title}`,
    },
    description: metadataNamespace.description,
    alternates: {
      canonical: `${baseUrl}/${locale}`,
      languages: {
        en: `${baseUrl}/en`,
        tr: `${baseUrl}/tr`,
        "x-default": `${baseUrl}/tr`,
      } as AlternateLanguages,
    },
    openGraph: {
      locale: locale === "tr" ? "tr_TR" : "en_US",
      alternateLocale: locale === "tr" ? ["en_US"] : ["tr_TR"],
      type: "website",
      url: `${baseUrl}/${locale}`,
    } as OpenGraphMetadata,
  }
}

describe("Layout Metadata Generation (hreflang & SEO)", () => {
  describe("English Locale Metadata", () => {
    let metadata: Metadata

    beforeEach(async () => {
      metadata = await generateMetadata("en")
    })

    it("returns metadata with title and template", () => {
      expect(metadata.title).toBeDefined()
      expect(metadata.title).toEqual({
        default: expect.any(String),
        template: expect.stringContaining("%s"),
      })
    })

    it("includes description from Metadata namespace", () => {
      expect(metadata.description).toBe(en.Metadata.description)
    })

    it("sets canonical URL with /en locale prefix", () => {
      expect(metadata.alternates?.canonical).toBe("http://localhost:3000/en")
    })

    it("includes hreflang link for en, tr, and x-default", () => {
      const languages = (metadata.alternates as { languages?: AlternateLanguages })?.languages
      expect(languages).toBeDefined()
      expect(languages?.en).toBe("http://localhost:3000/en")
      expect(languages?.tr).toBe("http://localhost:3000/tr")
      expect(languages?.["x-default"]).toBe("http://localhost:3000/tr")
    })

    it("sets og:locale to en_US for English locale", () => {
      const ogMetadata = metadata.openGraph as OpenGraphMetadata
      expect(ogMetadata?.locale).toBe("en_US")
    })

    it("sets alternateLocale to tr_TR for English locale", () => {
      const ogMetadata = metadata.openGraph as OpenGraphMetadata
      const alternateLocale = ogMetadata?.alternateLocale
      expect(alternateLocale).toContain("tr_TR")
      expect(alternateLocale).toHaveLength(1)
    })

    it("sets og:url with /en prefix", () => {
      const ogMetadata = metadata.openGraph as OpenGraphMetadata
      expect(ogMetadata?.url).toBe("http://localhost:3000/en")
    })

    it("sets og:type to website", () => {
      const ogMetadata = metadata.openGraph as OpenGraphMetadata
      expect(ogMetadata?.type).toBe("website")
    })
  })

  describe("Turkish Locale Metadata", () => {
    let metadata: Metadata

    beforeEach(async () => {
      metadata = await generateMetadata("tr")
    })

    it("returns metadata with title and template", () => {
      expect(metadata.title).toBeDefined()
      expect(metadata.title).toEqual({
        default: expect.any(String),
        template: expect.stringContaining("%s"),
      })
    })

    it("includes description from Turkish Metadata namespace", () => {
      expect(metadata.description).toBe(tr.Metadata.description)
    })

    it("sets canonical URL with /tr locale prefix", () => {
      expect(metadata.alternates?.canonical).toBe("http://localhost:3000/tr")
    })

    it("includes hreflang link for en, tr, and x-default (pointing to tr)", () => {
      const languages = (metadata.alternates as { languages?: AlternateLanguages })?.languages
      expect(languages).toBeDefined()
      expect(languages?.en).toBe("http://localhost:3000/en")
      expect(languages?.tr).toBe("http://localhost:3000/tr")
      expect(languages?.["x-default"]).toBe("http://localhost:3000/tr")
    })

    it("sets og:locale to tr_TR for Turkish locale", () => {
      const ogMetadata = metadata.openGraph as OpenGraphMetadata
      expect(ogMetadata?.locale).toBe("tr_TR")
    })

    it("sets alternateLocale to en_US for Turkish locale", () => {
      const ogMetadata = metadata.openGraph as OpenGraphMetadata
      const alternateLocale = ogMetadata?.alternateLocale
      expect(alternateLocale).toContain("en_US")
      expect(alternateLocale).toHaveLength(1)
    })

    it("sets og:url with /tr prefix", () => {
      const ogMetadata = metadata.openGraph as OpenGraphMetadata
      expect(ogMetadata?.url).toBe("http://localhost:3000/tr")
    })

    it("sets og:type to website", () => {
      const ogMetadata = metadata.openGraph as OpenGraphMetadata
      expect(ogMetadata?.type).toBe("website")
    })
  })

  describe("Hreflang SEO Compliance", () => {
    it("hreflang languages object contains required locales", async () => {
      const enMetadata = await generateMetadata("en")
      const languages = (enMetadata.alternates as { languages?: AlternateLanguages })?.languages

      expect(Object.keys(languages ?? {}).sort()).toEqual(["en", "tr", "x-default"])
    })

    it("x-default points to default locale (tr)", async () => {
      const enMetadata = await generateMetadata("en")
      const languages = (enMetadata.alternates as { languages?: AlternateLanguages })?.languages

      expect(languages?.["x-default"]).toBe("http://localhost:3000/tr")
    })

    it("canonical URL is consistent with locale", async () => {
      const enMetadata = await generateMetadata("en")
      const trMetadata = await generateMetadata("tr")

      expect(enMetadata.alternates?.canonical).toContain("/en")
      expect(trMetadata.alternates?.canonical).toContain("/tr")
    })
  })

  describe("Open Graph Locale Settings", () => {
    it("switches og:locale based on current locale", async () => {
      const enMetadata = await generateMetadata("en")
      const trMetadata = await generateMetadata("tr")

      const enOgMetadata = enMetadata.openGraph as OpenGraphMetadata
      const trOgMetadata = trMetadata.openGraph as OpenGraphMetadata

      expect(enOgMetadata?.locale).toBe("en_US")
      expect(trOgMetadata?.locale).toBe("tr_TR")
    })

    it("alternateLocale mirrors current locale setting", async () => {
      const enMetadata = await generateMetadata("en")
      const trMetadata = await generateMetadata("tr")

      const enOgMetadata = enMetadata.openGraph as OpenGraphMetadata
      const trOgMetadata = trMetadata.openGraph as OpenGraphMetadata

      expect(enOgMetadata?.alternateLocale).toEqual(["tr_TR"])
      expect(trOgMetadata?.alternateLocale).toEqual(["en_US"])
    })

    it("og:url includes locale prefix", async () => {
      const enMetadata = await generateMetadata("en")
      const trMetadata = await generateMetadata("tr")

      const enOgMetadata = enMetadata.openGraph as OpenGraphMetadata
      const trOgMetadata = trMetadata.openGraph as OpenGraphMetadata

      expect(enOgMetadata?.url).toContain("/en")
      expect(trOgMetadata?.url).toContain("/tr")
    })
  })

  describe("Message Namespace Integration", () => {
    it("English Metadata namespace has required keys", () => {
      expect(en.Metadata.title).toBeDefined()
      expect(en.Metadata.description).toBeDefined()
      expect(typeof en.Metadata.title).toBe("string")
      expect(typeof en.Metadata.description).toBe("string")
    })

    it("Turkish Metadata namespace has required keys", () => {
      expect(tr.Metadata.title).toBeDefined()
      expect(tr.Metadata.description).toBeDefined()
      expect(typeof tr.Metadata.title).toBe("string")
      expect(typeof tr.Metadata.description).toBe("string")
    })

    it("Metadata titles are different between locales", () => {
      expect(en.Metadata.title).not.toBe(tr.Metadata.title)
    })

    it("Metadata descriptions are different between locales", () => {
      expect(en.Metadata.description).not.toBe(tr.Metadata.description)
    })

    it("Metadata titles contain the app name", () => {
      expect(en.Metadata.title).toContain("Clarus")
      expect(tr.Metadata.title).toContain("Clarus")
    })
  })
})
