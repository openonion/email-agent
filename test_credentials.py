"""Test if Credentials work without client_id and client_secret."""
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load .env file
load_dotenv()

# Load tokens from env
access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")

print("Testing Credentials with client_id=None and client_secret=None...")
print(f"Access token (first 20 chars): {access_token[:20] if access_token else 'MISSING'}")
print(f"Refresh token (first 20 chars): {refresh_token[:20] if refresh_token else 'MISSING'}")
print()

# Create credentials WITHOUT client_id/client_secret
try:
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=None,
        client_secret=None,
        scopes=["https://www.googleapis.com/auth/gmail.readonly",
               "https://www.googleapis.com/auth/gmail.modify"]
    )
    print("✓ Credentials object created successfully with None values")
    print(f"  - token: {creds.token[:20]}..." if creds.token else "  - token: None")
    print(f"  - refresh_token: {creds.refresh_token[:20]}..." if creds.refresh_token else "  - refresh_token: None")
    print(f"  - client_id: {creds.client_id}")
    print(f"  - client_secret: {creds.client_secret}")
    print()

    # Try to build Gmail service
    service = build('gmail', 'v1', credentials=creds)
    print("✓ Gmail service built successfully")
    print()

    # Try to make an API call (this will fail due to Gmail API not enabled, but we'll see how far we get)
    print("Attempting to call Gmail API...")
    try:
        profile = service.users().getProfile(userId='me').execute()
        print(f"✓ API call successful! Email: {profile.get('emailAddress')}")
    except Exception as e:
        error_msg = str(e)
        if "Gmail API has not been used" in error_msg:
            print("✗ Gmail API not enabled (expected)")
            print("  But credentials with client_id=None worked up to this point!")
        elif "invalid_grant" in error_msg or "Token has been expired" in error_msg:
            print("✗ Token expired")
            print("  This is where our backend refresh would kick in")
        else:
            print(f"✗ Unexpected error: {error_msg}")

except Exception as e:
    print(f"✗ Failed to create credentials or service: {e}")
    import traceback
    traceback.print_exc()

print()
print("CONCLUSION:")
print("If we got 'Gmail service built successfully', then client_id=None works!")
print("The Gmail API error is a separate issue (API not enabled in Google Cloud).")
