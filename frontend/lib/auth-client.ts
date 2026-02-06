/**
 * Better Auth React Client
 * 
 * Configured with JWT plugin for token-based authentication.
 * Uses environment variable for baseURL to support different environments.
 * 
 * @see https://better-auth.com/docs/integrations/react
 */

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [jwtClient()],
});

export const { signIn, signUp, signOut, useSession, getSession } = authClient;
