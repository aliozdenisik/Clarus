import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"
import { nextCookies } from "better-auth/next-js"
import { polar, checkout, portal } from "@polar-sh/better-auth"
import { Polar } from "@polar-sh/sdk"
import { Pool } from "pg"
import bcrypt from "bcryptjs"
import { render } from "@react-email/render"
import { VerifyEmailTemplate } from "@/emails/verify-email"
import { ResetPasswordTemplate } from "@/emails/reset-password"
import { API_BASE } from "@/lib/config"
import { sendEmail } from "@/lib/email"

/**
 * Better Auth server instance configuration
 *
 * Features:
 * - Email/password auth with bcrypt (cost=12) for backend compatibility
 * - Google OAuth social provider
 * - JWT plugin for token generation and JWKS endpoints
 * - PostgreSQL database adapter (raw pg, not Prisma/Drizzle)
 * - 7-day session expiration, refreshed every 24 hours
 * - CORS protection with trustedOrigins
 *
 * @see https://better-auth.com/docs
 */

const polarClient = new Polar({
  accessToken: process.env.POLAR_ACCESS_TOKEN!,
  server: (process.env.POLAR_SERVER as "sandbox" | "production") || "sandbox",
})
export const auth = betterAuth({
  // PostgreSQL connection using pg package
  database: new Pool({
    connectionString:
      process.env.DATABASE_URL || "postgresql://postgres:postgres@localhost:54322/postgres",
  }),

  // Email and password authentication with bcrypt
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    resetPasswordTokenExpiresIn: 3600, // 1 hour (OWASP)
    password: {
      // Use bcrypt with cost=12 (matches backend for migration compatibility)
      hash: async (password) => {
        return await bcrypt.hash(password, 12)
      },
      verify: async ({ hash, password }) => {
        return await bcrypt.compare(password, hash)
      },
    },
    sendResetPassword: async ({ user, url }) => {
      void sendEmail({
        to: user.email,
        subject: "Clarus – Şifrenizi sıfırlayın / Reset your password",
        html: await render(
          ResetPasswordTemplate({ userName: user.name || user.email, actionUrl: url, locale: "tr" })
        ),
      })
    },
  },

  // Google OAuth social provider
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },

  emailVerification: {
    sendVerificationEmail: async ({ user, url }) => {
      void sendEmail({
        to: user.email,
        subject: "Clarus – E-postanızı doğrulayın / Verify your email",
        html: await render(
          VerifyEmailTemplate({ userName: user.name || user.email, actionUrl: url, locale: "tr" })
        ),
      })
    },
    sendOnSignUp: true,
    sendOnSignIn: true,
    autoSignInAfterVerification: true,
    expiresIn: 86400, // 24 hours
  },

  // Plugins: JWT for token generation, Polar for billing, nextCookies for Server Actions
  plugins: [
    jwt(), // Enables /api/auth/jwks and JWT token generation
    polar({
      client: polarClient,
      createCustomerOnSignUp: true,
      use: [
        checkout({
          products: [
            { productId: process.env.POLAR_PRO_PRODUCT_ID!, slug: "pro" },
            { productId: process.env.POLAR_STARTER_PRODUCT_ID!, slug: "starter" },
          ],
          successUrl: "/billing/success?checkout_id={CHECKOUT_ID}",
          authenticatedUsersOnly: true,
        }),
        portal(),
      ],
    }),
    nextCookies(), // MUST be last plugin - handles cookies in Server Actions
  ],

  // Session configuration
  session: {
    expiresIn: 7 * 24 * 60 * 60, // 7 days in seconds
    updateAge: 24 * 60 * 60, // Refresh every 1 day
  },

  // Security: CORS protection
  trustedOrigins: [
    process.env.NEXT_PUBLIC_FRONTEND_URL || "http://localhost:3000", // Frontend dev server
    API_BASE, // Backend API server
  ],

  // Base URL for redirects and callbacks
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
})
