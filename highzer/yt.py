import time
import json
from path import Path
from datetime import date, datetime
from opplast import Upload
from .utils import pretty_short_time, get_week, locate_folder, get_base_folder


def get_publish_date():
    now = datetime.utcnow()
    now = now.replace(hour=17, minute=0, second=0, microsecond=0)
    return now.isoformat() + "Z"


def save_video(ident, video_path, clips, category):
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
    tags.append(category.replace(' ', '').lower())
    tags.append('twitch')
    tags.append('highlight')
    tags.append(f'week{cw}')

    snippet = {
        "title": f"Week {cw} - {category} - Top {len(clips)} Twitch Highlights {year}",
        "description": description,
        "tags": tags,
    }

    with open(f"{folder}/data.json", "w+") as f:
        f.write(json.dumps(snippet))


# TODO maybe retry operator?
def upload_video(ident):
    profile = './profile'
    folder = locate_folder(ident)

    with open(f'{folder}/data.json', 'r') as f:
        raw = f.read()

    meta = json.loads(raw)
    meta['file'] = f'{folder}/merged.mp4'

    ff = Upload(Path(profile).abspath(), 5, True, True)
    uploaded, videoid = ff.upload(meta)
    if not uploaded:
        print('Video not uploaded!!', ident)
        return

    print(f'Uploaded Video: {ident} with ID: {videoid}')
