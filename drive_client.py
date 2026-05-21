"""Google Drive client: OAuth + folder/file operations."""
from __future__ import annotations

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

APP_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = APP_DIR / "credentials.json"
TOKEN_PATH = APP_DIR / "token.json"


class DriveClient:
    def __init__(self) -> None:
        self.service = build("drive", "v3", credentials=self._get_credentials())

    def _get_credentials(self) -> Credentials:
        creds: Credentials | None = None
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
            return creds
        if not CREDENTIALS_PATH.exists():
            raise FileNotFoundError(
                f"找不到 credentials.json，請依 README 步驟從 Google Cloud Console 下載，"
                f"並放在：{CREDENTIALS_PATH}"
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        return creds

    def get_or_create_folder(self, name: str, parent_id: str | None = None) -> str:
        """Return folder id, creating it under parent if missing."""
        escaped = name.replace("'", "\\'")
        query = (
            f"name = '{escaped}' "
            f"and mimeType = 'application/vnd.google-apps.folder' "
            f"and trashed = false"
        )
        if parent_id:
            query += f" and '{parent_id}' in parents"
        result = self.service.files().list(
            q=query, spaces="drive", fields="files(id, name)", pageSize=1
        ).execute()
        files = result.get("files", [])
        if files:
            return files[0]["id"]
        metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            metadata["parents"] = [parent_id]
        created = self.service.files().create(body=metadata, fields="id").execute()
        return created["id"]

    def upload_file(self, local_path: str, folder_id: str, display_name: str) -> str:
        media = MediaFileUpload(local_path, resumable=False)
        body = {"name": display_name, "parents": [folder_id]}
        result = self.service.files().create(
            body=body, media_body=media, fields="id"
        ).execute()
        return result["id"]

    def make_folder_link_shareable(self, folder_id: str) -> str:
        """Give anyone-with-link viewer access and return the share URL."""
        try:
            self.service.permissions().create(
                fileId=folder_id,
                body={"type": "anyone", "role": "reader"},
                fields="id",
            ).execute()
        except Exception:
            # Permission may already exist; ignore and just return the link.
            pass
        return f"https://drive.google.com/drive/folders/{folder_id}"
