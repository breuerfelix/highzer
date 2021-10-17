import os
import requests
import json
import time
from .utils import locate_folder, log
from .twitch import get_top_clips
from .movie import concat_clips
from .yt import save_video, upload_video


def get_clips(ident, period, game, channel, n = 0, limit = 30, duration = 5, force = False):
    folder = locate_folder(ident)
    filename = f"{folder}/clips.json"

    if not force and os.path.isfile(filename):
        log(ident, "Already downloaded clip info")
        return

    res = get_top_clips(period, game, channel, limit=limit)
    log(ident, f"Amount Top Clips: {len(res)}")

    # make video always x minutes long
    clips = filter_clips_duration(res, duration = duration)
    log(ident, f"Filtered Clips: {len(clips)}")

    # last clip is most viewed
    clips = sorted(clips, key=lambda x: x["views"])

    # save clips to file if process get stuck
    category = channel if channel else game
    data = dict(
        clips = clips,
        n = n,
        period = period,
        category = category,
    )
    with open(filename, "w+") as f:
        f.write(json.dumps(data))


def filter_clips_duration(clips, duration = 5):
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

def cut_clips(ident):
    folder = locate_folder(ident)

    with open(f"{folder}/clips.json", "r") as f:
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

    return data


def do_clips(games, period, n = 0, limit = 30, duration = 5):
    identifiers = list()
    for game in games:
        pg = game.replace(" ", "").lower()
        ident = f"{period[0]}{n}_{pg}"
        identifiers.append(ident)
        get_clips(ident, period, game, None, n, limit, duration)
        # sleep to prevent ddos to twitch
        time.sleep(5)

    for ident in identifiers:
        cut_clips(ident)
        save_video(ident)
        upload_video(ident)
        print(f"Finished Video: {ident}")


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
