import requests
from utils import pprint


def download_clip(slug, client_id="kimne78kx3ncx6brgo4mv6wki5h1ko"):
    url = f"https://api.twitch.tv/kraken/clips/{slug}"
    headers = {
        "Accept": "application/vnd.twitchtv.v5+json",
        "Client-ID": client_id,
    }

    clip_info = requests.get(url, headers=headers).json()

    thumb_url = clip_info["thumbnails"]["tiny"]
    mp4_url = thumb_url.split("-preview", 1)[0] + ".mp4"

    res = requests.get(mp4_url)

    out_filename = slug + ".mp4"
    with open(out_filename, "wb") as file:
        file.write(res.content)

    return out_filename


if __name__ == "__main__":
    download_clip("DarkAdorableAlmondPanicBasket")
