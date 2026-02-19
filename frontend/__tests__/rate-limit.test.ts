import { afterAll, beforeEach, describe, expect, it } from "vitest"

import {
  clearFixedWindowRateLimitState,
  consumeDistributedFixedWindow,
  consumeFixedWindow,
} from "@/lib/security/rate-limit"

const originalStreamProxyRedisUrl = process.env.STREAM_PROXY_REDIS_URL
const originalRedisUrl = process.env.REDIS_URL

describe("consumeFixedWindow", () => {
  beforeEach(() => {
    delete process.env.STREAM_PROXY_REDIS_URL
    delete process.env.REDIS_URL
    clearFixedWindowRateLimitState()
  })

  afterAll(() => {
    if (originalStreamProxyRedisUrl) {
      process.env.STREAM_PROXY_REDIS_URL = originalStreamProxyRedisUrl
    } else {
      delete process.env.STREAM_PROXY_REDIS_URL
    }

    if (originalRedisUrl) {
      process.env.REDIS_URL = originalRedisUrl
    } else {
      delete process.env.REDIS_URL
    }
  })

  it("allows requests until the limit is reached", () => {
    const first = consumeFixedWindow("search-ip", 2, 1_000, 0)
    const second = consumeFixedWindow("search-ip", 2, 1_000, 100)
    const third = consumeFixedWindow("search-ip", 2, 1_000, 200)

    expect(first.allowed).toBe(true)
    expect(first.remaining).toBe(1)

    expect(second.allowed).toBe(true)
    expect(second.remaining).toBe(0)

    expect(third.allowed).toBe(false)
    expect(third.retryAfterSeconds).toBe(1)
  })

  it("resets the bucket after the window expires", () => {
    consumeFixedWindow("compare-ip", 1, 1_000, 0)
    const blocked = consumeFixedWindow("compare-ip", 1, 1_000, 300)
    const allowedAfterReset = consumeFixedWindow("compare-ip", 1, 1_000, 1_001)

    expect(blocked.allowed).toBe(false)
    expect(allowedAfterReset.allowed).toBe(true)
    expect(allowedAfterReset.remaining).toBe(0)
  })

  it("throws for invalid limiter configuration", () => {
    expect(() => consumeFixedWindow("invalid", 0, 1_000, 0)).toThrow(
      "limit and windowMs must be positive"
    )
    expect(() => consumeFixedWindow("invalid", 1, 0, 0)).toThrow(
      "limit and windowMs must be positive"
    )
  })

  it("falls back to in-memory mode when redis is not configured", async () => {
    const first = await consumeDistributedFixedWindow("fallback-ip", 1, 1_000, 0)
    const second = await consumeDistributedFixedWindow("fallback-ip", 1, 1_000, 1)

    expect(first.allowed).toBe(true)
    expect(second.allowed).toBe(false)
    expect(second.retryAfterSeconds).toBe(1)
  })
})
