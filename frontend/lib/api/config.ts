import { client } from './client.gen';

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
 */
export function configureApiClient() {
  client.setConfig({
    auth: () => {
      // typeof window check: Next.js runs on both server (SSR) and client.
      // localStorage only exists in the browser. Without this check, SSR would
      // crash with "localStorage is not defined". Returning undefined means
      // "no auth token available" — the SDK simply omits the Authorization header.
      if (typeof window === 'undefined') return undefined;
      return localStorage.getItem('access_token') || undefined;
    },
  });
}
