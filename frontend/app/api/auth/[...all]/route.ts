/**
 * Better Auth Catch-All API Route Handler
 *
 * This route handles all Better Auth endpoints:
 * - POST /api/auth/sign-in/email
 * - POST /api/auth/sign-up/email
 * - POST /api/auth/sign-in/social
 * - POST /api/auth/sign-out
 * - GET /api/auth/session
 * - GET /api/auth/ok (health check)
 * - GET /api/auth/jwks (JWT public keys)
 * - GET /api/auth/callback/google (OAuth callback)
 *
 * @see https://better-auth.com/docs/installation#nextjs-app-router
 */

import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"

export const { GET, POST } = toNextJsHandler(auth)
