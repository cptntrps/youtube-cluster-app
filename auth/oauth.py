"""
YouTube API OAuth authentication module
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pathlib

# If modifying these scopes, delete your token file
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
TOKEN_FILE = 'token.pickle'
# Get the base directory of the application
BASE_DIR = pathlib.Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, 'client_secrets.json')

def authenticate():
    """
    Authenticate with the YouTube API using OAuth2
    
    Returns:
        googleapiclient.discovery.Resource: YouTube API service resource
    """
    creds = None
    
    # Check if token file exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If no credentials or they're invalid, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Get client secrets from environment or file
            client_id = os.getenv('YOUTUBE_CLIENT_ID')
            client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
            
            if client_id and client_secret:
                # Create flow from client secrets in environment variables
                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            else:
                # Fall back to client secrets file with absolute path
                print(f"Using client secrets from: {CLIENT_SECRETS_FILE}")
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    # Build and return the YouTube API service
    return build('youtube', 'v3', credentials=creds)
