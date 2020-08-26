from utils import pprint, locate_folder
from twitch import get_top_clips
from fpeg import concat, sample, merge, convert, concat_fast, cat
import requests


def cut_clips(ident, period, game, channel):
    res = get_top_clips(period, game, channel)

    # last clip is most viewed
    clips = sorted(res, key=lambda x: x["views"])

    folder = locate_folder(ident)

    files = []
    for clip in clips:
        raw_name = f"{folder}/{clip['slug']}"
        filename = f"{raw_name}.mp4"
        download_clip(clip, filename)
        # sample(filename)

        converted_name = f"{raw_name}.mpg"
        convert(filename, converted_name)
        filename = converted_name

        files.append(filename)

    # cat(files, f"{folder}/clip_merged.mpeg")
    # import os
    # concat([os.path.abspath(file) for file in files], os.path.abspath(f"{folder}/clip_merged.mp4"), os.path.abspath(f"{folder}/temp"))
    # concat(files, f"{folder}/clip_merged.mp4", f"{folder}/temp")
    # merge(files, f"{folder}/clip_merge.mp4")
    merged = f"{folder}/merged.mpg"
    concat_fast(files, merged)
    convert(merged, f"{folder}/merged.mp4")

    return clips, merged


def download_clip(clip, filename):
    thumb_url = clip["thumbnails"]["tiny"]
    mp4_url = thumb_url.split("-preview", 1)[0] + ".mp4"

    res = requests.get(mp4_url)
    with open(filename, "wb") as file:
        file.write(res.content)

    print(f"downloaded clip: {filename}")
    return filename
