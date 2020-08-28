from config import CLIENT_ID
import requests
import urllib.parse

HEADERS = {
    "Accept": "application/vnd.twitchtv.v5+json",
    "Client-ID": CLIENT_ID,
}


def get_top_clips(period, game, channel, limit=5, trending="false", language="en"):
    url = f"https://api.twitch.tv/kraken/clips/top?"
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
    return requests.get(url, headers=HEADERS).json()["clips"]


def get_clip_info(slug):
    url = f"https://api.twitch.tv/kraken/clips/{slug}"
    return requests.get(url, headers=HEADERS).json()
