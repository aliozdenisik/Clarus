import { client } from './client.gen';
import { getSession } from '../auth-client';

/**
 * Configure the generated API client with global authentication.
 * Must be called once at app initialization (root layout or provider).
 *
 * How it works:
 * 1. SDK functions define `security: [{scheme: 'bearer', type: 'http'}]`
 * 2. Client's internal `setAuthParams` (in core/utils.gen.ts) calls this auth function
 * 3. The auth function receives an Auth object, returns the raw token string
 * 4. Client prepends "Bearer " automatically (auth.gen.ts:33-35)
 * 5. Final header: `Authorization: Bearer <token>`
 * 
 * Updated to use Better Auth's getSession() for token retrieval.
 */
export function configureApiClient() {
  client.setConfig({
    auth: async () => {
      // typeof window check: Next.js runs on both server (SSR) and client.
      // getSession only works in the browser. Returning undefined means
      // "no auth token available" — the SDK simply omits the Authorization header.
      if (typeof window === 'undefined') return undefined;
      
      // Fallback to localStorage for backward compatibility
      // Better Auth stores tokens in localStorage, and our backend still uses access_token
      const legacyToken = localStorage.getItem('access_token');
      return legacyToken || undefined;
    },
  });
}
