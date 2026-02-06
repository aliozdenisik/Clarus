import { client } from './client.gen';

/**
 * Configure the generated API client with cookie-based authentication.
 * Must be called once at app initialization (root layout or provider).
 *
 * How it works:
 * - All requests include `credentials: 'include'` so the browser
 *   automatically sends the Better Auth session cookie.
 * - The backend's `get_current_user_flexible` validates the cookie first,
 *   then falls back to Bearer token / API key.
 * - No manual token management needed — the browser handles cookies.
 */
export function configureApiClient() {
  client.setConfig({
    // Send cookies with every request (Better Auth session cookie)
    credentials: 'include',
  });
}
