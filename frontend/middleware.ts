import createMiddleware from "next-intl/middleware"
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { routing } from "./i18n/routing"

const handleI18nRouting = createMiddleware(routing)

const protectedRoutes = ["/compare", "/search", "/settings", "/history", "/keyword-search"]

export function middleware(request: NextRequest) {
  const response = handleI18nRouting(request)

  const pathname = request.nextUrl.pathname
  const isProtectedRoute = protectedRoutes.some((route) => {
    const localePrefix = `/(en|tr)`
    return new RegExp(`^${localePrefix}${route}(/|$)`).test(pathname)
  })

  if (isProtectedRoute) {
    const sessionCookie = request.cookies.get("better-auth.session_token")

    if (!sessionCookie) {
      const locale = pathname.split("/")[1] || "tr"
      const signInUrl = new URL(`/${locale}/sign-in`, request.url)
      return NextResponse.redirect(signInUrl, { headers: response.headers })
    }
  }

  return response
}

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*|favicon.ico|monitoring).*)"],
}
