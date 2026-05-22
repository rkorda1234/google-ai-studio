"""One-time script to get your Google Ads refresh token.

Run this once: python3 get_google_token.py
It opens a browser, you approve access, and it prints your refresh token.
Copy that token into your .env file.
"""

import os
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import httpx

# ── Fill these in before running ─────────────────────────────────────────────
CLIENT_ID = input("Paste your Google OAuth Client ID: ").strip()
CLIENT_SECRET = input("Paste your Google OAuth Client Secret: ").strip()
# ─────────────────────────────────────────────────────────────────────────────

REDIRECT_URI = "http://localhost:8080"
SCOPE = "https://www.googleapis.com/auth/adwords"

auth_code = None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = parse_qs(urlparse(self.path).query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Success! You can close this tab and go back to the terminal.</h2>")

    def log_message(self, *args):
        pass  # silence server logs


def main():
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
        "&response_type=code"
        "&access_type=offline"
        "&prompt=consent"
    )

    print("\nOpening your browser to authorize Google Ads access...")
    print("(If it doesn't open automatically, copy this URL into your browser)")
    print(f"\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("Waiting for you to approve in the browser...")
    server = HTTPServer(("localhost", 8080), Handler)
    server.handle_request()

    if not auth_code:
        print("ERROR: No authorization code received.")
        sys.exit(1)

    # Exchange code for tokens
    r = httpx.post("https://oauth2.googleapis.com/token", data={
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    tokens = r.json()

    if "refresh_token" not in tokens:
        print(f"\nERROR: {tokens.get('error_description', tokens)}")
        sys.exit(1)

    print("\n" + "="*60)
    print("SUCCESS! Add these to your .env file:")
    print("="*60)
    print(f"GOOGLE_ADS_CLIENT_ID={CLIENT_ID}")
    print(f"GOOGLE_ADS_CLIENT_SECRET={CLIENT_SECRET}")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={tokens['refresh_token']}")
    print("="*60)


if __name__ == "__main__":
    main()
