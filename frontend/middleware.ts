import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const sessionCookie = request.cookies.get("better-auth.session_token")

  if (!sessionCookie) {
    // Redirect to sign-in page if no session cookie
    return NextResponse.redirect(new URL("/sign-in", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/compare", "/search", "/settings", "/history", "/keyword-search"],
}
