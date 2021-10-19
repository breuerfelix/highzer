import requests
import urllib.parse
import os
from .config import CLIENT_ID
from .utils import retry, locate_folder, run, log

HEADERS = {
    "Accept": "application/vnd.twitchtv.v5+json",
    "Client-ID": CLIENT_ID,
}

@retry
def get_top_clips(period, game, channel, limit=5, trending="false", language="en"):
    url = "https://api.twitch.tv/kraken/clips/top?"
    params = {
        "period": period,
        "trending": trending,
        "limit": limit,
        "language": language,
    }

    if game is not None:
        params["game"] = game

    if channel is not None:
        params["channel"] = channel

    url += urllib.parse.urlencode(params)
    res = requests.get(url, headers=HEADERS).json()
    return res["clips"]


def get_clip_info(slug):
    url = f"https://api.twitch.tv/kraken/clips/{slug}"
    return requests.get(url, headers=HEADERS).json()


def fetch_vod(ident, url):
    folder = locate_folder(ident)

    # create user folder
    if not os.path.exists(folder):
        os.makedirs(folder)

    id = url.split("/")[-1]

    # download chat
    log(ident, f"Fetching chat for VOD: {id}")
    run(
        "tcd", "--video", id, "--output", ident, "--format", "json",
    )
    os.rename(f"{folder}/{id}.json", f"{folder}/chat.json")

    # download VOD
    log(ident, f"Fetching VOD: {id}")
    run(
        "streamlink", "-o", f"{folder}/raw.ts", f"{url}", "best",
    )


def convert_vod(ident):
    folder = locate_folder(ident)

    log(ident, "Converting ts to mp4")
    run(
        "ffmpeg", "-i", f"{folder}/raw.ts", "-c", "copy", f"{folder}/raw.mp4",
    )

    os.remove(f"{folder}/raw.ts")
    log(ident, "Removed ts format")

    log(ident, "Extracting sound from mp4")
    run("ffmpeg", "-i", f"{folder}/raw.mp4", "-map", "0:a", f"{folder}/sound.mp3")
