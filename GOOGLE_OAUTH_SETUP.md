# Google OAuth Setup Guide

## Problem
You're getting "Error 401: invalid_client" and "no registered origin" when trying to sign in with Google.

## Solution

### Step 1: Create Google OAuth Client

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google+ API
   - Google Identity API
   - Google OAuth2 API

### Step 2: Create OAuth 2.0 Client ID

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. Choose **Web application**
4. Set the name (e.g., "Suna AI Local Development")

### Step 3: Configure Authorized Origins

Add these **Authorized JavaScript origins**:
```
http://localhost:3000
http://127.0.0.1:3000
```

### Step 4: Configure Redirect URIs

Add these **Authorized redirect URIs**:
```
http://localhost:3000/auth/callback
http://localhost:3000
```

### Step 5: Update Your Configuration

1. Copy your new **Client ID** from Google Cloud Console
2. Update the `.env` file in the `frontend` directory:

```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_actual_client_id_here
```

3. Restart your Docker containers:

```bash
docker-compose down
docker-compose up -d
```

## Alternative: Use Test Client ID

If you want to test quickly, you can try using this test client ID that should work with localhost:

```
NEXT_PUBLIC_GOOGLE_CLIENT_ID=56115052550-1sl7ppupetmqf8if9as6laeve6q1ic7g.apps.googleusercontent.com
```

But for production use, you should create your own client ID following the steps above.

## Troubleshooting

- Make sure your Google Cloud project has billing enabled
- Ensure the OAuth consent screen is configured
- Check that the APIs are enabled
- Verify the authorized origins exactly match your local URL
- Clear browser cache and cookies if needed

## Security Note

Never commit real client secrets to version control. The client ID is safe to expose, but client secrets should be kept secure.