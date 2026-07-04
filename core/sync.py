"""Post-session delivery: Google Drive upload + Gmail email of the PDF report.

Runs ONLY after a session ends (never mid-session). Requires an OAuth `credentials.json`
(Desktop app) in the project root; a `token.json` is created on first authorization.
On failure, callers should keep the local file and surface "Sync/Email pending".
"""
from __future__ import annotations

import base64
import mimetypes
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Union

from .config import settings

PathLike = Union[str, Path]

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/gmail.send",
]


def _creds():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None
    if settings.token_path.exists():
        creds = Credentials.from_authorized_user_file(str(settings.token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(settings.credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        settings.token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def upload_to_drive(path: PathLike) -> str:
    """Upload a file to Drive; return its shareable webViewLink (or id)."""
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    service = build("drive", "v3", credentials=_creds())
    path = Path(path)
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    media = MediaFileUpload(str(path), mimetype=mime)
    created = service.files().create(
        body={"name": path.name}, media_body=media, fields="id, webViewLink"
    ).execute()
    return created.get("webViewLink") or created.get("id", "")


def email_report(pdf_path: PathLike, subject: str, body: str,
                 to: Optional[list[str]] = None) -> None:
    """Email the PDF report to the parents via Gmail."""
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=_creds())
    recipients = to or list(settings.parent_emails)

    msg = EmailMessage()
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    pdf_path = Path(pdf_path)
    msg.add_attachment(
        pdf_path.read_bytes(), maintype="application", subtype="pdf", filename=pdf_path.name
    )

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
