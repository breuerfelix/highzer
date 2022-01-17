import os
import requests
import json
import time
from .utils import locate_folder, log, get_ident
from .twitch import get_top_clips
from .movie import concat_clips
from .yt import get_yt_snippet
from .upload import upload_ident


def do_clips(games, period, n = 0, limit = 30, duration = 5):
    identifiers = list()
    for game in games:
        ident = get_ident(game, period, n)
        done = fetch_clip_data(ident, period, game, None, limit, duration, n = n)

        if done:
            # only append identifier if we found enough clips
            identifiers.append(ident)

        # sleep to prevent ddos to twitch
        time.sleep(5)
    print("Finished fetching clips")

    for ident in identifiers:
        merge_clips(ident, ident)
    print("Finished merging clips")

    for ident in identifiers:
        upload_ident(ident, ident)
    print("Finished uploading videos")


def do_clip(game, period, n = 0, limit = 30, duration = 5):
    ident = get_ident(game, period, n)
    done = fetch_clip_data(ident, period, game, None, limit, duration, n = n)

    if not done:
        print("Not able to fetch clips")
        return

    print("Finished fetching clips")

    merge_clips(ident, ident)
    print("Finished merging clips")

    upload_ident(ident, ident)
    print("Finished uploading videos")


def fetch_clip_data(
    ident, period, game, channel,
    limit = 30, duration = 5, force = False,
    n = 0, **kwargs,
):
    folder = locate_folder(ident)
    filename = f"{folder}/meta.json"

    if not force and os.path.isfile(filename):
        log(ident, "Already saved meta information")
        return True

    try:
        res = get_top_clips(period, game, channel, limit=limit)
    except:
        log(ident, "Error getting clips")
        return False

    log(ident, f"Amount top clips: {len(res)}")
    if len(res) < 1:
        return False

    # make video always x minutes long
    clips = filter_clips_duration(res, duration = duration)
    log(ident, f"filtered clips: {len(clips)}")

    # first clip is most viewed
    clips = sorted(clips, reverse=True, key=lambda x: x["views"])

    category = channel if channel else game

    snippet = get_yt_snippet(clips, category, period, n)
    data = dict(
        clips = clips,
        period = period,
        category = category,
        n = n,
        # TODO why does the following line throw and error?
        #snippet = snippet,
        **kwargs,
    )
    data["snippet"] = snippet
    data["ident"] = get_ident(game, period, n)

    with open(filename, "w+") as f:
        json.dump(data, f)

    return True


def filter_clips_duration(clips, duration):
    """duration is time in minutes"""
    clips = sorted(clips, key=lambda x: x["views"], reverse=True)
    current_duration = 0
    max_duration = duration * 60

    filtered = []
    for clip in clips:
        if current_duration > max_duration: break
        current_duration += clip["duration"]
        filtered.append(clip)

    return filtered


def merge_clips(ident, meta):
    folder = locate_folder(ident)
    filename = f"{locate_folder(meta)}/meta.json"
    with open(filename, "r") as f:
        raw = f.read()

    data = json.loads(raw)
    clips = data["clips"]

    log(ident, f"Downloading {len(clips)} Clips")

    files = []

    for clip in clips:
        raw_name = f"{folder}/{clip['slug']}"
        filename = f"{raw_name}.mp4"
        download_clip(clip, filename)

        files.append(filename)

    out_file = f"{folder}/merged.mp4"
    concat_clips(files, out_file)
    return data["ident"]


def download_clip(clip, filename, force=False):
    if not force and os.path.isfile(filename):
        print("Clip already downloaded")
        return

    thumb_url = clip["thumbnails"]["tiny"]
    mp4_url = thumb_url.split("-preview", 1)[0] + ".mp4"

    res = requests.get(mp4_url)
    with open(filename, "wb") as file:
        file.write(res.content)

    print(f"Downloaded clip: {filename}")
    return filename
