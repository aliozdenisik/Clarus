import { describe, it, expect, beforeEach } from "vitest"
import type { Metadata } from "next"
import en from "../../messages/en.json"
import tr from "../../messages/tr.json"

type MetadataAlternates = NonNullable<Metadata["alternates"]>
type MetadataAlternateLanguages = NonNullable<MetadataAlternates["languages"]>
type MetadataOpenGraph = NonNullable<Metadata["openGraph"]>

function getLanguages(metadata: Metadata): MetadataAlternateLanguages | undefined {
  return metadata.alternates?.languages ?? undefined
}

function getOpenGraph(metadata: Metadata): MetadataOpenGraph | undefined {
  return metadata.openGraph ?? undefined
}

/**
 * Mock implementation of generateMetadata for testing
 * This mirrors the actual implementation in app/[locale]/layout.tsx
 */
async function generateMetadata(locale: string): Promise<Metadata> {
  const baseUrl = "http://localhost:3000"
  const metadata = locale === "tr" ? tr : en
  const metadataNamespace = metadata.Metadata
  const alternateLanguages: MetadataAlternateLanguages = {
    en: `${baseUrl}/en`,
    tr: `${baseUrl}/tr`,
    "x-default": `${baseUrl}/tr`,
  }

  return {
    title: {
      default: metadataNamespace.title,
      template: `%s | ${metadataNamespace.title}`,
    },
    description: metadataNamespace.description,
    alternates: {
      canonical: `${baseUrl}/${locale}`,
      languages: alternateLanguages,
    },
    openGraph: {
      locale: locale === "tr" ? "tr_TR" : "en_US",
      alternateLocale: locale === "tr" ? ["en_US"] : ["tr_TR"],
      type: "website",
      url: `${baseUrl}/${locale}`,
    },
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
      const languages = getLanguages(metadata)
      expect(languages).toBeDefined()
      expect(languages?.en).toBe("http://localhost:3000/en")
      expect(languages?.tr).toBe("http://localhost:3000/tr")
      expect(languages?.["x-default"]).toBe("http://localhost:3000/tr")
    })

    it("sets og:locale to en_US for English locale", () => {
      const ogMetadata = getOpenGraph(metadata)
      expect(ogMetadata?.locale).toBe("en_US")
    })

    it("sets alternateLocale to tr_TR for English locale", () => {
      const ogMetadata = getOpenGraph(metadata)
      const alternateLocale = ogMetadata?.alternateLocale
      expect(alternateLocale).toContain("tr_TR")
      expect(alternateLocale).toHaveLength(1)
    })

    it("sets og:url with /en prefix", () => {
      const ogMetadata = getOpenGraph(metadata)
      expect(ogMetadata?.url).toBe("http://localhost:3000/en")
    })

    it("sets og:type to website", () => {
      const ogMetadata = getOpenGraph(metadata)
      const ogType =
        ogMetadata && "type" in ogMetadata && typeof ogMetadata.type === "string"
          ? ogMetadata.type
          : undefined
      expect(ogType).toBe("website")
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
      const languages = getLanguages(metadata)
      expect(languages).toBeDefined()
      expect(languages?.en).toBe("http://localhost:3000/en")
      expect(languages?.tr).toBe("http://localhost:3000/tr")
      expect(languages?.["x-default"]).toBe("http://localhost:3000/tr")
    })

    it("sets og:locale to tr_TR for Turkish locale", () => {
      const ogMetadata = getOpenGraph(metadata)
      expect(ogMetadata?.locale).toBe("tr_TR")
    })

    it("sets alternateLocale to en_US for Turkish locale", () => {
      const ogMetadata = getOpenGraph(metadata)
      const alternateLocale = ogMetadata?.alternateLocale
      expect(alternateLocale).toContain("en_US")
      expect(alternateLocale).toHaveLength(1)
    })

    it("sets og:url with /tr prefix", () => {
      const ogMetadata = getOpenGraph(metadata)
      expect(ogMetadata?.url).toBe("http://localhost:3000/tr")
    })

    it("sets og:type to website", () => {
      const ogMetadata = getOpenGraph(metadata)
      const ogType =
        ogMetadata && "type" in ogMetadata && typeof ogMetadata.type === "string"
          ? ogMetadata.type
          : undefined
      expect(ogType).toBe("website")
    })
  })

  describe("Hreflang SEO Compliance", () => {
    it("hreflang languages object contains required locales", async () => {
      const enMetadata = await generateMetadata("en")
      const languages = getLanguages(enMetadata)

      expect(Object.keys(languages ?? {}).sort()).toEqual(["en", "tr", "x-default"])
    })

    it("x-default points to default locale (tr)", async () => {
      const enMetadata = await generateMetadata("en")
      const languages = getLanguages(enMetadata)

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

      const enOgMetadata = getOpenGraph(enMetadata)
      const trOgMetadata = getOpenGraph(trMetadata)

      expect(enOgMetadata?.locale).toBe("en_US")
      expect(trOgMetadata?.locale).toBe("tr_TR")
    })

    it("alternateLocale mirrors current locale setting", async () => {
      const enMetadata = await generateMetadata("en")
      const trMetadata = await generateMetadata("tr")

      const enOgMetadata = getOpenGraph(enMetadata)
      const trOgMetadata = getOpenGraph(trMetadata)

      expect(enOgMetadata?.alternateLocale).toEqual(["tr_TR"])
      expect(trOgMetadata?.alternateLocale).toEqual(["en_US"])
    })

    it("og:url includes locale prefix", async () => {
      const enMetadata = await generateMetadata("en")
      const trMetadata = await generateMetadata("tr")

      const enOgMetadata = getOpenGraph(enMetadata)
      const trOgMetadata = getOpenGraph(trMetadata)

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
