import os
import requests
import json
import time
from .utils import pprint, locate_folder, log, get_week
from .twitch import get_top_clips
from .fpeg import concat, sample, merge, convert, concat_fast, cat
from .movie import concat_clips
from .yt import save_video, upload_video


def get_clips(ident, period, game, channel):
    res = get_top_clips(period, game, channel, limit=30)
    log(ident, f"Amount Top Clips: {len(res)}")

    # make video always x minutes long
    clips = filter_clips_duration(res, duration = 4)
    log(ident, f"Filtered Clips: {len(clips)}")

    # last clip is most viewed
    clips = sorted(clips, key=lambda x: x["views"])

    folder = locate_folder(ident)
    # save clips to process if data got lost
    with open(f"{folder}/clips.json", "w+") as f:
        f.write(json.dumps(clips))


def filter_clips_duration(clips, duration = 4):
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

    clips = json.loads(raw)
    log(ident, f"Downloading {len(clips)} Clips")

    files = []

    for clip in clips:
        raw_name = f"{folder}/{clip['slug']}"
        filename = f"{raw_name}.mp4"
        download_clip(clip, filename)

        files.append(filename)

    out_file = f"{folder}/merged.mp4"
    concat_clips(files, out_file)

    game = clips[0]['game']
    return clips, out_file, game


def do_clips(games):
    week = get_week()
    identifiers = list()
    for game in games:
        pg = game.replace(" ", "").lower()
        ident = f"{week}_{pg}"
        identifiers.append(ident)
        get_clips(ident, 'week', game, None)
        # sleep to prevent ddos to twitch
        time.sleep(5)

    for ident in identifiers:
        clips, merged, game = cut_clips(ident)
        save_video(ident, merged, clips, game)
        upload_video(ident)
        print(f"uploaded video: {ident}")


def download_clip(clip, filename, force=False):
    if not force and os.path.isfile(filename):
        print("Clip already downloaded.")
        return

    thumb_url = clip["thumbnails"]["tiny"]
    mp4_url = thumb_url.split("-preview", 1)[0] + ".mp4"

    res = requests.get(mp4_url)
    with open(filename, "wb") as file:
        file.write(res.content)

    print(f"Downloaded clip: {filename}")
    return filename
