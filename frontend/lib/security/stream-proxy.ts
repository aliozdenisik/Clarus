const VALID_SEARCH_SOURCES = new Set<string>(["quran", "ot", "nt", "apocrypha"])

const VALID_TRANSLATORS = new Set<string>([
  "diyanet",
  "yazir",
  "ates",
  "bulac",
  "ozturk",
  "vakfi",
  "yildirim",
  "yuksel",
])

const VALID_COMPARE_COLLECTIONS = new Set<string>([
  "quran_tr",
  "bible_ot",
  "bible_nt",
  "bible_apocrypha",
])

const AUTH_COOKIE_NAMES = new Set<string>([
  "better-auth.session_token",
  "better_auth.session_token",
  "__Secure-better-auth.session_token",
])

const MAX_QUERY_LENGTH = 500
const MAX_USER_AGENT_LENGTH = 120

const LANGUAGE_PATTERN = /^[a-z]{2}(?:-[a-z]{2})?$/

const normalizeTextParam = (value: string | null, maxLength: number): string | null => {
  if (!value) {
    return null
  }

  const normalized = value.trim()
  if (!normalized) {
    return null
  }

  return normalized.slice(0, maxLength)
}

const normalizeLanguage = (value: string | null): string | null => {
  if (!value) {
    return null
  }

  const normalized = value.trim().toLowerCase()
  if (!normalized || !LANGUAGE_PATTERN.test(normalized)) {
    return null
  }

  return normalized
}

const normalizeKeywords = (value: string | null): string | null => {
  if (!value) {
    return null
  }

  const keywordTokens = value
    .split(",")
    .map((token) => token.trim())
    .filter(Boolean)
    .slice(0, 20)
    .map((token) => token.slice(0, 64))

  if (keywordTokens.length === 0) {
    return null
  }

  return keywordTokens.join(",")
}

export function buildSearchProxyParams(input: URLSearchParams): URLSearchParams {
  const params = new URLSearchParams()

  const query = normalizeTextParam(input.get("q"), MAX_QUERY_LENGTH)
  if (query) {
    params.set("q", query)
  }

  const source = input.get("source")?.trim().toLowerCase()
  if (source && VALID_SEARCH_SOURCES.has(source)) {
    params.set("source", source)
  }

  const language = normalizeLanguage(input.get("language"))
  if (language) {
    params.set("language", language)
  }

  const translator = input.get("translator")?.trim().toLowerCase()
  if (translator && VALID_TRANSLATORS.has(translator)) {
    params.set("translator", translator)
  }

  const keywords = normalizeKeywords(input.get("keywords"))
  if (keywords) {
    params.set("keywords", keywords)
  }

  return params
}

export function buildCompareProxyParams(input: URLSearchParams): URLSearchParams {
  const params = new URLSearchParams()

  const topic = normalizeTextParam(input.get("topic"), MAX_QUERY_LENGTH)
  if (topic) {
    params.set("topic", topic)
  }

  const rawCollections = input.get("collections")
  if (rawCollections) {
    const collections = rawCollections
      .split(",")
      .map((collection) => collection.trim())
      .filter((collection) => VALID_COMPARE_COLLECTIONS.has(collection))
      .slice(0, 4)

    if (collections.length > 0) {
      params.set("collections", collections.join(","))
    }
  }

  const language = normalizeLanguage(input.get("language"))
  if (language) {
    params.set("language", language)
  }

  const translator = input.get("translator")?.trim().toLowerCase()
  if (translator && VALID_TRANSLATORS.has(translator)) {
    params.set("translator", translator)
  }

  return params
}

export function buildAuthCookieHeader(rawCookieHeader: string): string {
  if (!rawCookieHeader) {
    return ""
  }

  const forwardedCookies: string[] = []

  for (const token of rawCookieHeader.split(";")) {
    const trimmed = token.trim()
    if (!trimmed) {
      continue
    }

    const separatorIndex = trimmed.indexOf("=")
    if (separatorIndex <= 0) {
      continue
    }

    const name = trimmed.slice(0, separatorIndex).trim()
    const value = trimmed.slice(separatorIndex + 1).trim()

    if (!value) {
      continue
    }

    if (AUTH_COOKIE_NAMES.has(name)) {
      forwardedCookies.push(`${name}=${value}`)
    }
  }

  return forwardedCookies.join("; ")
}

export function getClientIdentifier(headers: Headers): string {
  const forwardedFor = headers
    .get("x-forwarded-for")
    ?.split(",")
    .map((value) => value.trim())
    .find(Boolean)
  const realIp = headers.get("x-real-ip")?.trim()
  const ip = forwardedFor || realIp || "unknown"

  const userAgent = (headers.get("user-agent") || "unknown").trim().slice(0, MAX_USER_AGENT_LENGTH)

  return `${ip}:${userAgent}`
}

export function getClientErrorMessage(status: number): string {
  if (status === 401) {
    return "Unauthorized"
  }

  if (status === 403) {
    return "Forbidden"
  }

  if (status === 429) {
    return "Rate limit exceeded"
  }

  if (status >= 500) {
    return "Service temporarily unavailable"
  }

  return "Request failed"
}

export function truncateForLog(value: string, maxLength: number = 400): string {
  if (value.length <= maxLength) {
    return value
  }

  return `${value.slice(0, maxLength)}...`
}
