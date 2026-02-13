import { describe, it, expect } from "vitest"
import { routing } from "@/i18n/routing"

describe("i18n routing configuration", () => {
  it("has correct locales array", () => {
    expect(routing.locales).toEqual(["en", "tr"])
  })

  it("has correct default locale", () => {
    expect(routing.defaultLocale).toBe("tr")
  })

  it("has correct locale prefix setting", () => {
    expect(routing.localePrefix).toBe("always")
  })

  it("includes both en and tr locales", () => {
    expect(routing.locales).toContain("en")
    expect(routing.locales).toContain("tr")
  })

  it("has exactly 2 locales", () => {
    expect(routing.locales).toHaveLength(2)
  })
})
