"""
Gmail API Authentication Module
Handles OAuth2 authentication for Gmail API access
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from config import GMAIL_CREDENTIALS_FILE, GMAIL_TOKEN_FILE, GMAIL_SCOPES


def get_gmail_service():
    """
    Authenticate and return Gmail service object
    """
    creds = None
    
    # Check if token exists
    if os.path.exists(GMAIL_TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, GMAIL_SCOPES)
        except Exception as e:
            print(f"Warning: Could not load existing token: {e}")
            print("Will attempt to create a new token...")
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Token expired. Refreshing...")
                creds.refresh(Request())
                print("✓ Token refreshed successfully!")
            except RefreshError as e:
                print(f"Error refreshing token: {e}")
                print("Will need to re-authenticate...")
                creds = None
        
        if not creds or not creds.valid:
            if not os.path.exists(GMAIL_CREDENTIALS_FILE):
                print(f"Error: {GMAIL_CREDENTIALS_FILE} not found!")
                print("Please download your OAuth2 credentials from Google Cloud Console")
                print("and save it as 'credentials.json' in the project directory.")
                return None
            
            try:
                print("Starting OAuth flow...")
                print("A browser window will open for authentication.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    GMAIL_CREDENTIALS_FILE, GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
                print("✓ OAuth flow completed successfully!")
            except Exception as e:
                print(f"Error during OAuth flow: {e}")
                print("\nTroubleshooting tips:")
                print("1. Make sure you've added your email as a test user in OAuth consent screen")
                print("2. Verify Gmail API is enabled in your Google Cloud project")
                print("3. Check that credentials.json is valid and not corrupted")
                return None
        
        # Save the credentials for the next run
        try:
            with open(GMAIL_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            print(f"✓ Credentials saved to {GMAIL_TOKEN_FILE}")
        except Exception as e:
            print(f"Warning: Could not save token: {e}")
    
    # Build and return Gmail service
    try:
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building Gmail service: {e}")
        return None


if __name__ == '__main__':
    print("Authenticating with Gmail API...")
    print(f"Using credentials file: {GMAIL_CREDENTIALS_FILE}")
    print(f"Scope: {GMAIL_SCOPES[0]}\n")
    
    service = get_gmail_service()
    if service:
        print("\n✓ Authentication successful!")
        print("Token saved to token.json")
        print("You can now use the Gmail API.")
    else:
        print("\n✗ Authentication failed!")
        print("Please check the error messages above and try again.")

