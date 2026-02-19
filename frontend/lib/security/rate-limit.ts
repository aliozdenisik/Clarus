import Redis from "ioredis"

type RateLimitBucket = {
  count: number
  resetAt: number
}

export type FixedWindowRateLimitResult = {
  allowed: boolean
  remaining: number
  retryAfterSeconds: number
  resetAt: number
}

const buckets = new Map<string, RateLimitBucket>()

const RATE_LIMIT_REDIS_PREFIX = "clarus:stream:rate"
const REDIS_RETRY_COOLDOWN_MS = 10_000
const REDIS_SCRIPT = `
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('PEXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('PTTL', KEYS[1])
if ttl < 0 then
  redis.call('PEXPIRE', KEYS[1], ARGV[1])
  ttl = tonumber(ARGV[1])
end
return {current, ttl}
`

let redisClient: Redis | null = null
let redisUnavailableUntil = 0

const CLEANUP_INTERVAL_MS = 60_000
let lastCleanupAt = 0

const getRedisUrl = (): string | null => {
  const configuredUrl = process.env.STREAM_PROXY_REDIS_URL || process.env.REDIS_URL || ""
  return configuredUrl.trim() || null
}

const getRedisClient = (now: number): Redis | null => {
  if (now < redisUnavailableUntil) {
    return null
  }

  const redisUrl = getRedisUrl()
  if (!redisUrl) {
    return null
  }

  if (!redisClient) {
    redisClient = new Redis(redisUrl, {
      maxRetriesPerRequest: 1,
      enableReadyCheck: false,
      lazyConnect: true,
    })
  }

  return redisClient
}

const markRedisUnavailable = (now: number): void => {
  redisUnavailableUntil = now + REDIS_RETRY_COOLDOWN_MS
  if (redisClient) {
    redisClient.disconnect()
    redisClient = null
  }
}

const toNumber = (value: unknown): number | null => {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : null
  }

  if (typeof value === "string") {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : null
  }

  return null
}

const parseRedisEvalResult = (value: unknown): { count: number; ttlMs: number } | null => {
  if (!Array.isArray(value) || value.length < 2) {
    return null
  }

  const count = toNumber(value[0])
  const ttlMs = toNumber(value[1])
  if (count === null || ttlMs === null) {
    return null
  }

  return {
    count,
    ttlMs,
  }
}

const buildResult = (
  count: number,
  limit: number,
  resetAt: number,
  now: number
): FixedWindowRateLimitResult => {
  const allowed = count <= limit
  const remaining = allowed ? Math.max(limit - count, 0) : 0
  const retryAfterSeconds = allowed ? 0 : Math.max(Math.ceil((resetAt - now) / 1000), 1)

  return {
    allowed,
    remaining,
    retryAfterSeconds,
    resetAt,
  }
}

const buildRedisRateLimitKey = (key: string): string => `${RATE_LIMIT_REDIS_PREFIX}:${key}`

const cleanupExpiredBuckets = (now: number): void => {
  if (now - lastCleanupAt < CLEANUP_INTERVAL_MS) {
    return
  }

  for (const [key, bucket] of buckets.entries()) {
    if (bucket.resetAt <= now) {
      buckets.delete(key)
    }
  }

  lastCleanupAt = now
}

export function consumeFixedWindow(
  key: string,
  limit: number,
  windowMs: number,
  now: number = Date.now()
): FixedWindowRateLimitResult {
  if (limit <= 0 || windowMs <= 0) {
    throw new Error("limit and windowMs must be positive")
  }

  cleanupExpiredBuckets(now)

  const current = buckets.get(key)
  if (!current || current.resetAt <= now) {
    const resetAt = now + windowMs
    buckets.set(key, { count: 1, resetAt })
    return {
      allowed: true,
      remaining: Math.max(limit - 1, 0),
      retryAfterSeconds: 0,
      resetAt,
    }
  }

  if (current.count >= limit) {
    return {
      allowed: false,
      remaining: 0,
      retryAfterSeconds: Math.max(Math.ceil((current.resetAt - now) / 1000), 1),
      resetAt: current.resetAt,
    }
  }

  current.count += 1
  return buildResult(current.count, limit, current.resetAt, now)
}

export async function consumeDistributedFixedWindow(
  key: string,
  limit: number,
  windowMs: number,
  now: number = Date.now()
): Promise<FixedWindowRateLimitResult> {
  if (limit <= 0 || windowMs <= 0) {
    throw new Error("limit and windowMs must be positive")
  }

  const redis = getRedisClient(now)
  if (!redis) {
    return consumeFixedWindow(key, limit, windowMs, now)
  }

  try {
    if (redis.status === "wait") {
      await redis.connect()
    }

    const rawResult = await redis.eval(REDIS_SCRIPT, 1, buildRedisRateLimitKey(key), String(windowMs))
    const parsed = parseRedisEvalResult(rawResult)
    if (!parsed) {
      return consumeFixedWindow(key, limit, windowMs, now)
    }

    const ttlMs = Math.max(parsed.ttlMs, 1)
    return buildResult(parsed.count, limit, now + ttlMs, now)
  } catch {
    markRedisUnavailable(now)
    return consumeFixedWindow(key, limit, windowMs, now)
  }
}

export function clearFixedWindowRateLimitState(): void {
  buckets.clear()
  lastCleanupAt = 0
  redisUnavailableUntil = 0
}
