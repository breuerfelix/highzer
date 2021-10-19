import json
import datetime

import google.oauth2.credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "client.json"

SCOPES = ["https://www.googleapis.com/auth/youtube"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


def get_api():
    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)

    expiry = datetime.datetime.fromisoformat(data["expiry"])
    creds = google.oauth2.credentials.Credentials(
        data["access_token"],
        refresh_token=data["refresh_token"],
        id_token=data["id_token"],
        token_uri=data["token_uri"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        scopes=data["scopes"],
        expiry=expiry,
    )

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)



def authenticate_api():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_console()

    creds_data = {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "id_token": creds.id_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
        "expiry": str(creds.expiry),
    }

    with open(TOKEN_FILE, "w+") as f:
        json.dump(creds_data, f)

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)



def update(youtube, id, title, description, tags):
    res = youtube.videos().list(id=id, part="snippet,status").execute()

    if not res["items"]:
        print("error: video not found")
        return False

    snippet = res["items"][0]["snippet"]
    snippet["title"] = title
    snippet["description"] = description
    snippet["tags"] = tags

    status = res["items"][0]["status"]
    status["privacyStatus"] = "public"

    body = dict(
        id = id,
        snippet = snippet,
        status = status,
    )

    youtube.videos().update(part="snippet,status", body=body).execute()
    return True
