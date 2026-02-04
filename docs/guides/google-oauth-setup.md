# Google OAuth Setup Guide

This guide explains how to configure Google OAuth for Clarus development environment.

## Prerequisites

- Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- Clarus backend running on `localhost:8000`
- Clarus frontend running on `localhost:3000`

## Step 1: Create Google Cloud Project (if needed)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown (top-left, next to "Google Cloud")
3. Click "New Project"
4. Name: `Clarus Development`
5. Click "Create"
6. Wait for project creation, then select it

## Step 2: Configure OAuth Consent Screen

1. In the sidebar, go to **APIs & Services** > **OAuth consent screen**
2. Select **External** (allows any Google account to sign in)
3. Click "Create"
4. Fill in required fields:
   - **App name**: `Clarus`
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click "Save and Continue"
6. **Scopes**: Click "Add or Remove Scopes"
   - Select: `email`, `profile`, `openid`
   - Click "Update"
7. Click "Save and Continue"
8. **Test users**: Add your Google email address
9. Click "Save and Continue"
10. Review and click "Back to Dashboard"

## Step 3: Create OAuth 2.0 Credentials

1. In the sidebar, go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth 2.0 Client ID**
3. Application type: **Web application**
4. Name: `Clarus Web Client`
5. **Authorized JavaScript origins**:
   - Add: `http://localhost:3000`
6. **Authorized redirect URIs**:
   - Add: `http://localhost:3000`
   - Add: `http://localhost:8000/api/auth/google/callback`
7. Click "Create"
8. A popup shows your credentials:
   - **Client ID**: `123456789-abc.apps.googleusercontent.com`
   - **Client Secret**: `GOCSPX-abc123...`
9. **Save these values** - you'll need them next

## Step 4: Configure Backend Environment

1. Open `backend/.env` in your editor
2. Find and update these lines:
   ```env
   GOOGLE_CLIENT_ID=your-client-id-from-step-3
   GOOGLE_CLIENT_SECRET=your-client-secret-from-step-3
   ```
3. Save the file
4. Restart the backend:
   ```bash
   uvicorn app.main:app --reload
   ```

## Step 5: Configure Frontend Environment

1. Create or edit `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id-from-step-3
   ```
   
   **Note**: Only the Client ID is needed for frontend. The secret stays in backend only.

2. Restart the frontend:
   ```bash
   cd frontend && npm run dev
   ```

## Step 6: Test the Integration

1. Open http://localhost:3000/login
2. Click "Sign in with Google"
3. Select your Google account in the popup
4. You should be redirected to `/search` and logged in

## Troubleshooting

### Error: `redirect_uri_mismatch`

**Cause**: The redirect URI in your request doesn't match any URI in Google Console.

**Solution**:
1. Go to Google Console > Credentials > Your OAuth Client
2. Check "Authorized redirect URIs"
3. Ensure exact match (no trailing slash, correct port)
4. Add missing URIs: `http://localhost:3000` and `http://localhost:8000/api/auth/google/callback`

### Error: `invalid_client`

**Cause**: Client ID or Secret is wrong.

**Solution**:
1. Go to Google Console > Credentials
2. Click on your OAuth client
3. Copy Client ID and Secret again
4. Paste into `backend/.env` and `frontend/.env.local`
5. **Check for spaces** - credentials should have no leading/trailing spaces

### Error: `access_denied`

**Cause**: User cancelled the consent screen.

**Solution**: This is normal behavior. No action needed.

### Popup blocked

**Cause**: Browser is blocking the Google popup.

**Solution**: 
1. Click the popup blocker icon in browser address bar
2. Allow popups for `localhost:3000`

### Error: `Google login failed. Please try again.`

**Cause**: Backend rejected the credential.

**Solution**:
1. Check backend logs for detailed error
2. Verify `GOOGLE_CLIENT_SECRET` in `backend/.env`
3. Ensure backend is running and accessible

## Security Notes

- **Client ID is public**: It's safe to expose in frontend code
- **Client Secret is private**: Never commit to git or expose in frontend
- **`.env` files**: Add to `.gitignore` (already configured)
- **Production**: Will need separate credentials with production URLs

## Production Setup (Future)

When production domain is ready:
1. Add production URLs to Google Console:
   - Authorized JavaScript origins: `https://your-domain.com`
   - Authorized redirect URIs: `https://your-domain.com`, `https://api.your-domain.com/api/auth/google/callback`
2. Create separate OAuth client for production (recommended)
3. Update production environment variables
