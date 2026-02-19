import { describe, expect, it } from "vitest"

import {
  buildAuthCookieHeader,
  buildCompareProxyParams,
  buildSearchProxyParams,
  getClientErrorMessage,
  getClientIdentifier,
} from "@/lib/security/stream-proxy"

describe("buildSearchProxyParams", () => {
  it("keeps only allowed and validated search params", () => {
    const params = new URLSearchParams([
      ["q", " sabir ve namaz "],
      ["source", "quran"],
      ["language", "TR"],
      ["translator", "Diyanet"],
      ["keywords", " sabir, namaz , , zikir "],
      ["admin", "1"],
    ])

    const result = buildSearchProxyParams(params)

    expect(result.get("q")).toBe("sabir ve namaz")
    expect(result.get("source")).toBe("quran")
    expect(result.get("language")).toBe("tr")
    expect(result.get("translator")).toBe("diyanet")
    expect(result.get("keywords")).toBe("sabir,namaz,zikir")
    expect(result.get("admin")).toBeNull()
  })

  it("drops invalid source, language, and translator values", () => {
    const params = new URLSearchParams([
      ["q", "topic"],
      ["source", "internal"],
      ["language", "turkish"],
      ["translator", "custom"],
    ])

    const result = buildSearchProxyParams(params)

    expect(result.get("q")).toBe("topic")
    expect(result.get("source")).toBeNull()
    expect(result.get("language")).toBeNull()
    expect(result.get("translator")).toBeNull()
  })
})

describe("buildCompareProxyParams", () => {
  it("keeps only allowed compare params", () => {
    const params = new URLSearchParams([
      ["topic", "yaratilis"],
      ["collections", "quran_tr,bible_ot,bible_nt,bible_apocrypha,unknown"],
      ["language", "EN"],
      ["translator", "Yazir"],
      ["debug", "true"],
    ])

    const result = buildCompareProxyParams(params)

    expect(result.get("topic")).toBe("yaratilis")
    expect(result.get("collections")).toBe("quran_tr,bible_ot,bible_nt,bible_apocrypha")
    expect(result.get("language")).toBe("en")
    expect(result.get("translator")).toBe("yazir")
    expect(result.get("debug")).toBeNull()
  })
})

describe("buildAuthCookieHeader", () => {
  it("forwards only auth cookies", () => {
    const rawCookieHeader =
      "theme=dark; better-auth.session_token=abc123; __Secure-better-auth.session_token=secure456; foo=bar"

    const result = buildAuthCookieHeader(rawCookieHeader)

    expect(result).toBe(
      "better-auth.session_token=abc123; __Secure-better-auth.session_token=secure456"
    )
  })
})

describe("getClientIdentifier", () => {
  it("builds a stable identifier using forwarded ip and user agent", () => {
    const headers = new Headers({
      "x-forwarded-for": "203.0.113.10, 10.0.0.4",
      "user-agent": "Vitest Agent",
    })

    expect(getClientIdentifier(headers)).toBe("203.0.113.10:Vitest Agent")
  })
})

describe("getClientErrorMessage", () => {
  it("maps backend status codes to safe client messages", () => {
    expect(getClientErrorMessage(401)).toBe("Unauthorized")
    expect(getClientErrorMessage(429)).toBe("Rate limit exceeded")
    expect(getClientErrorMessage(503)).toBe("Service temporarily unavailable")
    expect(getClientErrorMessage(400)).toBe("Request failed")
  })
})
