import os
from utils import pprint, locate_folder
from twitch import get_top_clips
from fpeg import concat, sample, merge, convert, concat_fast, cat
import requests
from movie import concat_clips


def cut_clips(ident, period, game, channel):
    res = get_top_clips(period, game, channel)
    print("Received TOP clips")

    # last clip is most viewed
    clips = sorted(res, key=lambda x: x["views"])

    folder = locate_folder(ident)

    files = []
    for clip in clips:
        raw_name = f"{folder}/{clip['slug']}"
        filename = f"{raw_name}.mp4"
        download_clip(clip, filename)

        files.append(filename)

    out_file = f"{folder}/merged.mp4"
    concat_clips(files, out_file)

    return clips, out_file


def download_clip(clip, filename, force=False):
    if not force and os.path.isfile(filename):
        print("Clip already downloaded.")
        return

    thumb_url = clip["thumbnails"]["tiny"]
    mp4_url = thumb_url.split("-preview", 1)[0] + ".mp4"

    print(f"Downloading clip: {filename}")
    res = requests.get(mp4_url)
    with open(filename, "wb") as file:
        file.write(res.content)

    print(f"Downloaded clip: {filename}")
    return filename


if __name__ == '__main__':
    cut_clips('testing', 'week', 'League of Legends', None)
