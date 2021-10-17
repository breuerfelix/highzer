import time
import json
from path import Path
from datetime import date, datetime
from opplast import Upload
from selenium.webdriver import FirefoxProfile, FirefoxOptions
from .utils import pretty_short_time, locate_folder, now
from .api import get_api, update_video


def get_publish_date():
    now = datetime.utcnow()
    now = now.replace(hour=17, minute=0, second=0, microsecond=0)
    return now.isoformat() + "Z"


def save_video(ident):
    folder = locate_folder(ident)

    with open(f"{folder}/clips.json", "r") as f:
        raw = f.read()

    data = json.loads(raw)
    clips = data["clips"]
    category = data["category"]
    period = data["period"]
    n = data["n"]

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

    year = date.today().year

    tags = [tag.lower() for tag in tags]
    tags.append(category.replace(' ', '').lower())
    tags.append('twitch')
    tags.append('highlight')
    tags.append(f'{period}{n}')

    # those chars throw errors with the youtube API
    invalid_chars = "<>"
    for char in invalid_chars:
        description = description.replace(char, "")

    snippet = {
        "title": f"{period.capitalize()} {n} - {category} - Top {len(clips)} Twitch Highlights {year}",
        "description": description,
        "tags": tags,
    }

    with open(f"{folder}/data.json", "w+") as f:
        f.write(json.dumps(snippet))


def upload_video(ident):
    profile_path = Path('./profile').abspath()
    profile = FirefoxProfile(profile_path)
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/94.0.4606.81 Safari/537.36"
    )
    profile.set_preference("general.useragent.override", user_agent)
    profile.set_preference("intl.accept_languages", "en-US")
    # mute audio
    profile.set_preference("media.volume_scale", "0.0")
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference("useAutomationExtension", False)
    profile.update_preferences()

    options = FirefoxOptions()
    options.add_argument("window-size=1920,1080")

    folder = locate_folder(ident)

    with open(f'{folder}/data.json', 'r') as f:
        raw = f.read()

    meta = json.loads(raw)
    meta['file'] = Path(f'{folder}/merged.mp4').abspath()

    counter = 1

    videoid = None
    while counter < 4:
        print(f'Uploading attempt: {counter}')
        ff = Upload(profile, timeout=7, options=options)

        try:
            uploaded, videoid = ff.upload(meta['file'], only_upload=True)

            if not uploaded:
                print(f'Video {ident} not uploaded, skipping')

            print(f'Uploaded Video: {ident} with ID: {videoid}')
            ff.close()
            break
        except:
            print('Video uploaded failed')
            stamp = str(now()).replace(".", "-")
            filepath = f'{folder}/error_{stamp}'
            ff.driver.save_screenshot(Path(filepath + '.png').abspath())

            with open(Path(filepath + '.html').abspath(), "w+") as f:
                f.write(ff.driver.find_element_by_xpath('//html').get_attribute('outerHTML'))

        ff.close()
        time.sleep(10)
        counter += 1

    if videoid is None:
        print("Error: videoid is none")
        return

    yt = get_api()
    done = update_video(yt, videoid, meta["title"], meta["description"], meta["tags"])
    if not done:
        print("Error: Could not update video")

    print(f"Video meta data for {meta['title']} changed")
