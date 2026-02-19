import createMiddleware from "next-intl/middleware"
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { routing } from "./i18n/routing"

const handleI18nRouting = createMiddleware(routing)

const protectedRoutes = ["/compare", "/search", "/settings", "/history", "/hub"]

export function middleware(request: NextRequest) {
  const response = handleI18nRouting(request)

  // Bot detection for SEO crawlability
  const userAgent = request.headers.get("user-agent") || ""
  const botPattern =
    /googlebot|bingbot|yandex|baiduspider|duckduckbot|facebookexternalhit|twitterbot|linkedinbot|slackbot|whatsapp|telegrambot|gptbot|claudebot|anthropic-ai|perplexitybot/i
  const isBot = botPattern.test(userAgent)

  const pathname = request.nextUrl.pathname
  const locale = pathname.split("/")[1] || "tr"
  const sessionCookie = request.cookies.get("better-auth.session_token")

  // Redirect authenticated users from root locale paths to /hub
  const rootLocalePathPattern = /^\/(en|tr)(?:\/|$)/
  if (rootLocalePathPattern.test(pathname) && pathname === `/${locale}`) {
    if (sessionCookie && !isBot) {
      const hubUrl = new URL(`/${locale}/hub`, request.url)
      return NextResponse.redirect(hubUrl, { headers: response.headers })
    }
  }

  const isProtectedRoute = protectedRoutes.some((route) => {
    const localePrefix = `/(en|tr)`
    return new RegExp(`^${localePrefix}${route}(/|$)`).test(pathname)
  })

  if (isProtectedRoute && !isBot) {
    if (!sessionCookie) {
      const signInUrl = new URL(`/${locale}/sign-in`, request.url)
      return NextResponse.redirect(signInUrl, { headers: response.headers })
    }
  }

  return response
}

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*|favicon.ico|monitoring).*)"],
}
