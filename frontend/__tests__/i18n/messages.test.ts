import { describe, test, expect } from "vitest"
import en from "../../messages/en.json"
import tr from "../../messages/tr.json"

/**
 * Recursively extract all keys from a nested object
 * Returns flat array of dot-notation keys (e.g., "Common.loading", "Landing.hero.title")
 */
function getKeys(obj: Record<string, unknown>, prefix = ""): string[] {
  return Object.entries(obj).flatMap(([key, value]) => {
    const fullKey = prefix ? `${prefix}.${key}` : key
    if (typeof value === "object" && value !== null && !Array.isArray(value)) {
      return getKeys(value as Record<string, unknown>, fullKey)
    }
    return [fullKey]
  })
}

/**
 * Recursively get all values from a nested object
 * Returns array of [key, value] tuples
 */
function getValues(obj: Record<string, unknown>, prefix = ""): Array<[string, unknown]> {
  return Object.entries(obj).flatMap(([key, value]) => {
    const fullKey = prefix ? `${prefix}.${key}` : key
    if (typeof value === "object" && value !== null && !Array.isArray(value)) {
      return getValues(value as Record<string, unknown>, fullKey)
    }
    return [[fullKey, value]] as Array<[string, unknown]>
  })
}

describe("i18n Message Catalogs", () => {
  describe("Key Structure Parity", () => {
    test("en.json and tr.json have identical key structures", () => {
      const enKeys = getKeys(en).sort()
      const trKeys = getKeys(tr).sort()

      // Check arrays are equal
      expect(enKeys).toEqual(trKeys)

      // Additional check: ensure count matches
      expect(enKeys.length).toBe(trKeys.length)
    })

    test("all top-level namespaces match", () => {
      const enNamespaces = Object.keys(en).sort()
      const trNamespaces = Object.keys(tr).sort()

      expect(enNamespaces).toEqual(trNamespaces)
    })

    test("Common namespace has identical keys", () => {
      const enCommonKeys = Object.keys(en.Common).sort()
      const trCommonKeys = Object.keys(tr.Common).sort()

      expect(enCommonKeys).toEqual(trCommonKeys)
    })

    test("Landing namespace structure matches", () => {
      const enLandingKeys = getKeys(en.Landing).sort()
      const trLandingKeys = getKeys(tr.Landing).sort()

      expect(enLandingKeys).toEqual(trLandingKeys)
    })
  })

  describe("Value Quality", () => {
    test("no empty string values in en.json", () => {
      const values = getValues(en)
      const emptyValues = values.filter(([, value]) => value === "")

      expect(emptyValues).toEqual([])
    })

    test("no empty string values in tr.json", () => {
      const values = getValues(tr)
      const emptyValues = values.filter(([, value]) => value === "")

      expect(emptyValues).toEqual([])
    })

    test("all en.json values are strings", () => {
      const values = getValues(en)
      const nonStringValues = values.filter(([, value]) => typeof value !== "string")

      expect(nonStringValues).toEqual([])
    })

    test("all tr.json values are strings", () => {
      const values = getValues(tr)
      const nonStringValues = values.filter(([, value]) => typeof value !== "string")

      expect(nonStringValues).toEqual([])
    })
  })

  describe("Namespace Coverage", () => {
    test("has all required namespaces", () => {
      const requiredNamespaces = [
        "Common",
        "Navigation",
        "Landing",
        "Search",
        "Compare",
        "Settings",
        "Auth",
        "KeywordSearch",
        "VerseLookup",
        "History",
        "Toast",
        "Errors",
        "Metadata",
        "Bible",
        "Quran",
      ]

      const enNamespaces = Object.keys(en)

      requiredNamespaces.forEach((namespace) => {
        expect(enNamespaces).toContain(namespace)
      })
    })

    test("has at least 200 total keys", () => {
      const enKeys = getKeys(en)
      expect(enKeys.length).toBeGreaterThanOrEqual(200)
    })
  })

  describe("ICU Format Validation", () => {
    test("ICU format strings have matching braces", () => {
      const values = getValues(en)
      const icuValues = values.filter(
        ([, value]) => typeof value === "string" && (value.includes("{") || value.includes("}"))
      )

      icuValues.forEach(([, value]) => {
        const str = value as string
        const openCount = (str.match(/{/g) || []).length
        const closeCount = (str.match(/}/g) || []).length

        expect(openCount).toBe(closeCount)
      })
    })

    test("plural forms are valid", () => {
      const values = getValues(en)
      const pluralValues = values.filter(
        ([, value]) => typeof value === "string" && value.includes("plural")
      )

      pluralValues.forEach(([, value]) => {
        const str = value as string
        // Check that plural has at least one variant (=0, =1, other)
        expect(str).toMatch(/=\d+|other/)
      })
    })
  })

  describe("Translation Quality (Turkish)", () => {
    test("Turkish translations use proper Turkish characters", () => {
      // Check a few key Turkish strings have Turkish characters (ğ, ü, ş, ı, ö, ç, İ)
      expect(tr.Common.loading).toContain("ü") // Yükleniyor
      expect(tr.Settings.confirmReset).toContain("ı") // sıfırlamak
      expect(tr.Toast.networkError).toContain("ğ") // Ağ hatası
    })

    test("Turkish translations are not just English copies", () => {
      // Sample check: ensure Turkish is different from English
      expect(tr.Common.loading).not.toBe(en.Common.loading)
      expect(tr.Common.search).not.toBe(en.Common.search)
      expect(tr.Landing.hero.title).not.toBe(en.Landing.hero.title)
    })
  })
})
