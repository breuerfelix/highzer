from oauth2client.client import flow_from_clientsecrets
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import httplib2
import sys
import random
import time
from datetime import date
from utils import pretty_short_time, get_week

SCOPE = "https://www.googleapis.com/auth/youtube.upload"


def upload_video(video_path, clips, cat):
    service = get_service()
    description = ""

    tags = []
    duration = 0.0
    for clip in clips:
        pt = pretty_short_time(int(duration))

        # remove newlines in titles
        title = clip["title"].split("\n")[0]
        description += f"{pt} - {title}\n"

        tags.append(clip["broadcaster"]["display_name"])
        duration += clip["duration"]

    cw = get_week()
    tags = [tag.lower() for tag in tags]
    tags = " ".join(tags)

    snippet = {
        "title": f"Week {cw} - {cat} - Top {len(clips)} Twitch Highlights",
        "description": description,
        "tags": f"twitch highlight week{cw} {cat.replace(' ', '').lower()} {tags}",
    }

    upload(service, video_path, snippet)


def get_service():
    flow = flow_from_clientsecrets("client_secrets.json", scope=SCOPE)
    storage = Storage("oauth2.json")
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, ["--noauth_local_webserver"])

    cred = credentials.authorize(httplib2.Http())
    service = build("youtube", "v3", http=cred)
    return service


def upload(service, video_path, snippet):
    snippet["categoryId"] = "20"
    body = {
        "snippet": snippet,
        "status": {"privacyStatus": "public",},
    }

    insert_request = service.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
    )

    resumable_upload(insert_request)


# TODO handle upload better
def resumable_upload(insert_request, max_retries=10):
    httplib2.RETRIES = 1
    RETRIABLE_EXCEPTIONS = (
        httplib2.HttpLib2Error,
        IOError,
    )
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if "id" in response:
                    print("Video id '%s' was successfully uploaded." % response["id"])
                    break
                else:
                    print(response)
                    sys.exit(
                        "The upload failed with an unexpected response: %s" % response
                    )
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred."
            print(e)
        if error is not None:
            print(error)
            retry += 1
            if retry > max_retries:
                sys.exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)


if __name__ == "__main__":
    youtube = get_service()
    upload_video(youtube, "data/test/merged.mp4")
    pass
