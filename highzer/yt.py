import time
import json
from path import Path
from datetime import date, datetime
from opplast import Upload
from .utils import pretty_short_time, get_week, locate_folder, now


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


def upload_video(ident):
    profile = './profile'
    folder = locate_folder(ident)

    with open(f'{folder}/data.json', 'r') as f:
        raw = f.read()

    meta = json.loads(raw)
    meta['file'] = Path(f'{folder}/merged.mp4').abspath()

    counter = 1

    while counter < 4:
        print(f'Uploading attempt: {counter}')
        ff = Upload(Path(profile).abspath(), "geckodriver", 10, True, True)

        try:
            uploaded, videoid = ff.upload(meta['file'], meta['title'], meta['description'], "", meta['tags'])
            ff.close()

            if not uploaded:
                print(f'Video {ident} not uploaded, skipping')

            print(f'Uploaded Video: {ident} with ID: {videoid}')
            break
        except:
            print('Video uploaded failed.')
            stamp = str(now()).replace(".", "-")
            filepath = f'{folder}/error_{stamp}'
            ff.driver.save_screenshot(Path(filepath + '.png').abspath())

            with open(Path(filepath + '.html').abspath(), "w+") as f:
                f.write(ff.driver.find_element_by_xpath('//html').get_attribute('outerHTML'))


        ff.close()
        time.sleep(10)
        counter += 1
