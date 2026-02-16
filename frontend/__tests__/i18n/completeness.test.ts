import { describe, test, expect } from "vitest"
import en from "../../messages/en.json"
import tr from "../../messages/tr.json"

/**
 * Recursively flatten nested object into dot-notation keys with their values
 * Returns array of {key, enValue, trValue, enType, trType, depth}
 */
function flattenForComparison(
  enObj: Record<string, unknown>,
  trObj: Record<string, unknown>,
  prefix = ""
): Array<{
  key: string
  enValue: unknown
  trValue: unknown
  enType: string
  trType: string
  depth: number
  enExists: boolean
  trExists: boolean
}> {
  const results: Array<{
    key: string
    enValue: unknown
    trValue: unknown
    enType: string
    trType: string
    depth: number
    enExists: boolean
    trExists: boolean
  }> = []

  // Get all possible keys from both objects
  const allKeys = new Set<string>()
  const enKeys = Object.keys(enObj)
  const trKeys = Object.keys(trObj)
  enKeys.forEach((k) => allKeys.add(k))
  trKeys.forEach((k) => allKeys.add(k))

  allKeys.forEach((key) => {
    const fullKey = prefix ? `${prefix}.${key}` : key
    const enValue = enObj[key]
    const trValue = trObj[key]
    const depth = fullKey.split(".").length

    const enIsObj = typeof enValue === "object" && enValue !== null && !Array.isArray(enValue)
    const trIsObj = typeof trValue === "object" && trValue !== null && !Array.isArray(trValue)

    if (enIsObj && trIsObj) {
      // Recurse into nested objects
      results.push(
        ...flattenForComparison(
          enValue as Record<string, unknown>,
          trValue as Record<string, unknown>,
          fullKey
        )
      )
    } else {
      // Leaf node - record the value
      results.push({
        key: fullKey,
        enValue,
        trValue,
        enType: typeof enValue,
        trType: typeof trValue,
        depth,
        enExists: key in enObj,
        trExists: key in trObj,
      })
    }
  })

  return results
}

/**
 * Extract all string values from a nested object
 */
function getAllStringValues(
  obj: Record<string, unknown>,
  prefix = ""
): Array<{ key: string; value: string }> {
  const results: Array<{ key: string; value: string }> = []

  Object.entries(obj).forEach(([key, value]) => {
    const fullKey = prefix ? `${prefix}.${key}` : key

    if (typeof value === "string") {
      results.push({ key: fullKey, value })
    } else if (typeof value === "object" && value !== null && !Array.isArray(value)) {
      results.push(...getAllStringValues(value as Record<string, unknown>, fullKey))
    }
  })

  return results
}

describe("Translation Completeness & Quality", () => {
  describe("Deep Key Structure Comparison with Diagnostics", () => {
    test("all keys present in both en.json and tr.json with detailed mismatch reporting", () => {
      const comparison = flattenForComparison(en, tr)
      const missingInTr = comparison.filter((c) => c.enExists && !c.trExists)
      const missingInEn = comparison.filter((c) => !c.enExists && c.trExists)
      const typeMismatches = comparison.filter((c) => c.enType !== c.trType)

      const errors: string[] = []

      if (missingInTr.length > 0) {
        errors.push(
          `Missing in tr.json (${missingInTr.length} keys): ${missingInTr.map((m) => m.key).join(", ")}`
        )
      }

      if (missingInEn.length > 0) {
        errors.push(
          `Missing in en.json (${missingInEn.length} keys): ${missingInEn.map((m) => m.key).join(", ")}`
        )
      }

      if (typeMismatches.length > 0) {
        errors.push(
          `Type mismatches (${typeMismatches.length} keys):\n${typeMismatches
            .map((m) => `  ${m.key}: en=${m.enType}, tr=${m.trType}`)
            .join("\n")}`
        )
      }

      expect(errors).toEqual([])
    })

    test("no type mismatches between locales", () => {
      const comparison = flattenForComparison(en, tr)
      const typeMismatches = comparison.filter(
        (c) => c.enType !== c.trType && c.enExists && c.trExists
      )

      if (typeMismatches.length > 0) {
        const details = typeMismatches
          .map((m) => `${m.key}: en is ${m.enType}, tr is ${m.trType}`)
          .join("\n")
        expect.fail(`Found type mismatches:\n${details}`)
      }

      expect(typeMismatches).toHaveLength(0)
    })

    test("all namespace depths are consistent", () => {
      const comparison = flattenForComparison(en, tr)
      const depths = new Set(comparison.map((c) => c.depth))

      // Should have reasonable depth distribution (1-3 levels typically)
      expect(Math.max(...depths)).toBeLessThanOrEqual(5)
      expect(Math.min(...depths)).toBeGreaterThanOrEqual(1)
    })
  })

  describe("Empty & Invalid Values", () => {
    test("no empty string values in either locale (comprehensive check)", () => {
      const enStrings = getAllStringValues(en)
      const trStrings = getAllStringValues(tr)

      const enEmpty = enStrings.filter((s) => s.value === "")
      const trEmpty = trStrings.filter((s) => s.value === "")

      const errors: string[] = []
      if (enEmpty.length > 0) {
        errors.push(`Empty values in en.json: ${enEmpty.map((e) => e.key).join(", ")}`)
      }
      if (trEmpty.length > 0) {
        errors.push(`Empty values in tr.json: ${trEmpty.map((e) => e.key).join(", ")}`)
      }

      expect(errors).toEqual([])
    })

    test("no null or undefined values in either locale", () => {
      const comparison = flattenForComparison(en, tr)

      const enNulls = comparison.filter((c) => c.enValue === null || c.enValue === undefined)
      const trNulls = comparison.filter((c) => c.trValue === null || c.trValue === undefined)

      const errors: string[] = []
      if (enNulls.length > 0) {
        errors.push(`Null/undefined in en.json: ${enNulls.map((n) => n.key).join(", ")}`)
      }
      if (trNulls.length > 0) {
        errors.push(`Null/undefined in tr.json: ${trNulls.map((n) => n.key).join(", ")}`)
      }

      expect(errors).toEqual([])
    })
  })

  describe("Hardcoded String Detection", () => {
    test("no hardcoded URLs in message strings (excluding example placeholders)", () => {
      const enStrings = getAllStringValues(en)
      const trStrings = getAllStringValues(tr)

      const urlPattern = /(https?:\/\/|www\.|\.com|\.org|\.io)/i
      const examplePlaceholderPattern = /(example|placeholder|sample|demo|you@|ornek@)/i

      const enUrlMatches = enStrings.filter(
        (s) => urlPattern.test(s.value) && !examplePlaceholderPattern.test(s.value)
      )
      const trUrlMatches = trStrings.filter(
        (s) => urlPattern.test(s.value) && !examplePlaceholderPattern.test(s.value)
      )

      const errors: string[] = []
      if (enUrlMatches.length > 0) {
        errors.push(
          `Hardcoded URLs in en.json: ${enUrlMatches.map((u) => `${u.key}="${u.value}"`).join("; ")}`
        )
      }
      if (trUrlMatches.length > 0) {
        errors.push(
          `Hardcoded URLs in tr.json: ${trUrlMatches.map((u) => `${u.key}="${u.value}"`).join("; ")}`
        )
      }

      expect(errors).toEqual([])
    })

    test("no hardcoded email addresses in message strings (excluding example placeholders)", () => {
      const enStrings = getAllStringValues(en)
      const trStrings = getAllStringValues(tr)

      const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/
      const examplePlaceholderPattern = /(example|placeholder|sample|demo|you@|ornek@)/i

      const enEmailMatches = enStrings.filter(
        (s) => emailPattern.test(s.value) && !examplePlaceholderPattern.test(s.value)
      )
      const trEmailMatches = trStrings.filter(
        (s) => emailPattern.test(s.value) && !examplePlaceholderPattern.test(s.value)
      )

      const errors: string[] = []
      if (enEmailMatches.length > 0) {
        errors.push(
          `Hardcoded emails in en.json: ${enEmailMatches.map((e) => `${e.key}="${e.value}"`).join("; ")}`
        )
      }
      if (trEmailMatches.length > 0) {
        errors.push(
          `Hardcoded emails in tr.json: ${trEmailMatches.map((e) => `${e.key}="${e.value}"`).join("; ")}`
        )
      }

      expect(errors).toEqual([])
    })

    test("no hardcoded API paths or ports in message strings", () => {
      const enStrings = getAllStringValues(en)
      const trStrings = getAllStringValues(tr)

      const apiPattern = /\/api\/|:80\d{2}|:3\d{3}|localhost|127\.0\.0\.1/
      const enApiMatches = enStrings.filter((s) => apiPattern.test(s.value))
      const trApiMatches = trStrings.filter((s) => apiPattern.test(s.value))

      const errors: string[] = []
      if (enApiMatches.length > 0) {
        errors.push(
          `Hardcoded API paths in en.json: ${enApiMatches.map((a) => `${a.key}="${a.value}"`).join("; ")}`
        )
      }
      if (trApiMatches.length > 0) {
        errors.push(
          `Hardcoded API paths in tr.json: ${trApiMatches.map((a) => `${a.key}="${a.value}"`).join("; ")}`
        )
      }

      expect(errors).toEqual([])
    })

    test("no suspiciously long strings (likely parameter values)", () => {
      const enStrings = getAllStringValues(en)
      const trStrings = getAllStringValues(tr)

      // Strings longer than 500 chars are suspicious in i18n
      const MAX_REASONABLE_LENGTH = 500
      const enLongStrings = enStrings.filter((s) => s.value.length > MAX_REASONABLE_LENGTH)
      const trLongStrings = trStrings.filter((s) => s.value.length > MAX_REASONABLE_LENGTH)

      const errors: string[] = []
      if (enLongStrings.length > 0) {
        errors.push(
          `Suspiciously long strings in en.json (${enLongStrings.length}): ${enLongStrings.map((s) => `${s.key} (${s.value.length} chars)`).join("; ")}`
        )
      }
      if (trLongStrings.length > 0) {
        errors.push(
          `Suspiciously long strings in tr.json (${trLongStrings.length}): ${trLongStrings.map((s) => `${s.key} (${s.value.length} chars)`).join("; ")}`
        )
      }

      expect(errors).toEqual([])
    })
  })

  describe("ICU Format Consistency (Supplementary)", () => {
    test("all ICU format strings have matching braces in both locales", () => {
      const enStrings = getAllStringValues(en)
      const trStrings = getAllStringValues(tr)

      const checkBraces = (strings: Array<{ key: string; value: string }>) => {
        return strings
          .filter((s) => s.value.includes("{") || s.value.includes("}"))
          .filter((s) => {
            const openCount = (s.value.match(/{/g) || []).length
            const closeCount = (s.value.match(/}/g) || []).length
            return openCount !== closeCount
          })
      }

      const enMismatches = checkBraces(enStrings)
      const trMismatches = checkBraces(trStrings)

      const errors: string[] = []
      if (enMismatches.length > 0) {
        errors.push(`ICU brace mismatches in en.json: ${enMismatches.map((m) => m.key).join(", ")}`)
      }
      if (trMismatches.length > 0) {
        errors.push(`ICU brace mismatches in tr.json: ${trMismatches.map((m) => m.key).join(", ")}`)
      }

      expect(errors).toEqual([])
    })

    test("ICU format variable names are identical between locales", () => {
      const enStrings = getAllStringValues(en)
      const trStrings = getAllStringValues(tr)

      // Extract variable names from ICU format strings {variableName}
      const extractVariables = (str: string): string[] => {
        const matches = str.match(/{(\w+)[,}]/g)
        return matches ? matches.map((m) => m.slice(1, -1).split(",")[0]) : []
      }

      const errors: string[] = []

      enStrings.forEach((enStr) => {
        const trStr = trStrings.find((t) => t.key === enStr.key)
        if (!trStr) return

        const enVars = extractVariables(enStr.value)
        const trVars = extractVariables(trStr.value)

        if (JSON.stringify(enVars.sort()) !== JSON.stringify(trVars.sort())) {
          errors.push(
            `Variable mismatch in ${enStr.key}: en={${enVars.join(", ")}}, tr={${trVars.join(", ")}}`
          )
        }
      })

      expect(errors).toEqual([])
    })
  })

  describe("Namespace Exhaustiveness (Supplementary)", () => {
    test("top-level namespace count matches", () => {
      const enNamespaces = Object.keys(en).sort()
      const trNamespaces = Object.keys(tr).sort()

      expect(enNamespaces.length).toBe(trNamespaces.length)
      expect(enNamespaces).toEqual(trNamespaces)
    })

    test("each namespace has at least 2 keys (not empty namespaces)", () => {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      Object.entries(en).forEach(([_namespace, content]) => {
        if (typeof content === "object" && content !== null && !Array.isArray(content)) {
          const keyCount = Object.keys(content).length
          expect(keyCount).toBeGreaterThanOrEqual(2)
        }
      })
    })
  })

  describe("Translation Consistency", () => {
    test("no keys with identical English and Turkish values (likely untranslated)", () => {
      const enStrings = getAllStringValues(en)
      const suspiciousMatches: Array<{ key: string; value: string }> = []

      enStrings.forEach((enStr) => {
        const trStr = getAllStringValues(tr).find((t) => t.key === enStr.key)
        if (trStr && enStr.value === trStr.value) {
          // Skip obvious cases: proper nouns, numbers, symbols, collection IDs, language names, translator names
          const isLikelyProperNoun = /^[A-Z][a-z]+$/.test(enStr.value)
          const isNumber = /^\d+$/.test(enStr.value)
          const isAbbreviation =
            enStr.value.length <= 3 && enStr.value.toUpperCase() === enStr.value
          const isCommonSymbol = /^[.,!?\-()•]+$/.test(enStr.value)
          const isCollectionName = /^(quran_tr|bible_|tr_)/i.test(enStr.value)
          const isLanguageName = /^(English|Türkçe|العربية)$/.test(enStr.value)
          const isPaddingChars = /^[•:\-\s]+$/.test(enStr.value)
          const isSystemIdentifier = enStr.value.length <= 20 && /^[a-z_]+$/.test(enStr.value)

          if (
            !isLikelyProperNoun &&
            !isNumber &&
            !isAbbreviation &&
            !isCommonSymbol &&
            !isCollectionName &&
            !isLanguageName &&
            !isPaddingChars &&
            !isSystemIdentifier
          ) {
            suspiciousMatches.push({ key: enStr.key, value: enStr.value })
          }
        }
      })

      // Reasonable threshold: allow up to 20 identical values (proper nouns, system identifiers, etc.)
      if (suspiciousMatches.length > 20) {
        const details = suspiciousMatches.map((m) => `${m.key}: "${m.value}"`).join("\n")
        expect.fail(`Found ${suspiciousMatches.length} potentially untranslated keys:\n${details}`)
      }
    })

    test("all numeric values in translations are identical", () => {
      const enStrings = getAllStringValues(en)
      const mismatches: string[] = []

      enStrings.forEach((enStr) => {
        const trStr = getAllStringValues(tr).find((t) => t.key === enStr.key)
        if (!trStr) return

        // Extract numbers from both
        const enNumbers = (enStr.value.match(/\d+/g) || []).sort()
        const trNumbers = (trStr.value.match(/\d+/g) || []).sort()

        if (JSON.stringify(enNumbers) !== JSON.stringify(trNumbers)) {
          mismatches.push(`${enStr.key}: en=${enNumbers}, tr=${trNumbers}`)
        }
      })

      expect(mismatches).toEqual([])
    })
  })
})
