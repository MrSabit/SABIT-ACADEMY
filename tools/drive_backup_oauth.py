import argparse
import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/drive"]


def build_drive_service():
    client_secret = os.environ.get("GDRIVE_CLIENT_SECRET_JSON")
    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN")
    if not client_secret:
        raise RuntimeError("Missing GDRIVE_CLIENT_SECRET_JSON")
    if not refresh_token:
        raise RuntimeError("Missing GDRIVE_REFRESH_TOKEN")

    info = json.loads(client_secret)
    creds = Credentials.from_authorized_user_info(
        {"refresh_token": refresh_token, "token": None, "client_id": info["installed"]["client_id"], "client_secret": info["installed"]["client_secret"]},
        SCOPES,
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)


def upload_file(service, folder_id: str, file_path: str, remote_name: str) -> str:
    file_metadata = {"name": remote_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    created = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    return created["id"]


def enforce_retention(service, folder_id: str, name_prefix: str, keep_last: int) -> int:
    if keep_last <= 0:
        return 0

    q = (
        f"'{folder_id}' in parents and trashed=false and name contains '{name_prefix}'"
    )
    files = []
    page_token = None
    while True:
        resp = (
            service.files()
            .list(
                q=q,
                spaces="drive",
                fields="nextPageToken, files(id,name,createdTime)",
                orderBy="createdTime desc",
                pageSize=1000,
                pageToken=page_token,
            )
            .execute()
        )
        files.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    deleted = 0
    for f in files[keep_last:]:
        service.files().delete(fileId=f["id"]).execute()
        deleted += 1
    return deleted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--folder", required=False, default=os.environ.get("GDRIVE_FOLDER_ID"))
    parser.add_argument("--name", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--keep-last", type=int, default=int(os.environ.get("GDRIVE_KEEP_LAST", "30")))
    args = parser.parse_args()

    if not args.folder:
        raise RuntimeError("Missing GDRIVE_FOLDER_ID")

    service = build_drive_service()
    upload_file(service, args.folder, args.file, args.name)
    enforce_retention(service, args.folder, args.prefix, args.keep_last)


if __name__ == "__main__":
    main()
