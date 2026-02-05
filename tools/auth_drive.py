import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]
CLIENT_SECRET_PATH = "client_secret.json"

def main():
    if not os.path.exists(CLIENT_SECRET_PATH):
        print(f"Error: {CLIENT_SECRET_PATH} not found. Download OAuth client JSON and rename to {CLIENT_SECRET_PATH}")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    print("\n=== REFRESH TOKEN (copy this to GitHub Secrets GDRIVE_REFRESH_TOKEN) ===")
    print(creds.refresh_token)
    print("=== END REFRESH TOKEN ===\n")
    print("Now add this as a GitHub Secret named GDRIVE_REFRESH_TOKEN")

if __name__ == "__main__":
    main()
