import time
import json
from datetime import date, datetime
from utils import pretty_short_time, get_week, locate_folder, get_base_folder


def get_publish_date():
    now = datetime.utcnow()
    now = now.replace(hour=17, minute=0, second=0, microsecond=0)
    return now.isoformat() + "Z"


def save_video(ident, video_path, clips, cat, upload=False):
    folder = locate_folder(ident)

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
    year = date.today().year

    tags = [tag.lower() for tag in tags]
    tags = " ".join(tags)

    snippet = {
        "title": f"Week {cw} - {cat} - Top {len(clips)} Twitch Highlights {year}",
        "description": description,
        "tags": f"twitch highlight week{cw} {cat.replace(' ', '').lower()} {tags}",
    }

    with open(f"{folder}/data.json", "w+") as f:
        f.write(json.dumps(snippet))


    with open(f"{get_base_folder()}/latest.txt", "w+") as f:
        f.write(ident)
