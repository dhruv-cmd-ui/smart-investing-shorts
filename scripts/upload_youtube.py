"""Uploads the rendered video to YouTube as a Short, using a one-time OAuth token.

This needs a one-time manual authorization (see README) because YouTube uploads act on
your personal channel — after that first authorization, the saved token refreshes itself
automatically and no further manual steps are needed.
"""
import argparse
import json
import os
import pickle
from pathlib import Path

GOOGLE_CLIENT_SECRET_PATH = Path(__file__).resolve().parent.parent / "config" / "youtube_client_secret.json"
TOKEN_PATH = Path(__file__).resolve().parent.parent / "config" / "youtube_token.pickle"
MANIFEST_PATH = Path(__file__).resolve().parent.parent / "remotion-project" / "public" / "audio" / "manifest.json"
VIDEO_PATH = Path(__file__).resolve().parent.parent / "remotion-project" / "out" / "video.mp4"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_authenticated_service():
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    credentials = None
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, "rb") as f:
            credentials = pickle.load(f)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(GOOGLE_CLIENT_SECRET_PATH), SCOPES)
            credentials = flow.run_local_server(port=0)
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(credentials, f)

    return build("youtube", "v3", credentials=credentials)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Build the upload request but don't actually call the API")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    title = manifest["hook"][:95] + " #Shorts"
    description = (
        f"{manifest['script']}\n\n"
        "Educational content only — not investment advice. Not a SEBI-registered advisor. "
        "Please consult a certified financial advisor before investing.\n\n"
        "#SmartInvestingIndia #PersonalFinance #Shorts"
    )

    print("Title:", title)
    print("Description:", description)
    print("Video file:", VIDEO_PATH)

    if args.dry_run:
        print("Dry run — not uploading.")
        return

    if not VIDEO_PATH.exists():
        raise FileNotFoundError(f"No rendered video at {VIDEO_PATH} — run the Remotion render first.")

    from googleapiclient.http import MediaFileUpload

    youtube = get_authenticated_service()
    body = {
        "snippet": {"title": title, "description": description, "categoryId": "27"},  # 27 = Education
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(VIDEO_PATH), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print(f"Uploaded: https://youtube.com/watch?v={response['id']}")


if __name__ == "__main__":
    main()
