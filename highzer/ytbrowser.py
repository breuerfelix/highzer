import time
from path import Path
from opplast import Upload
from selenium.webdriver import FirefoxProfile, FirefoxOptions
from .utils import locate_folder, now, log


def upload(ident):
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
    video_file_path = Path(f'{folder}/merged.mp4').abspath()

    counter = 1
    videoid = None
    while counter < 4:
        log(ident, f'Uploading attempt: {counter}')
        ff = Upload(profile, timeout=7, options=options)

        try:
            uploaded, videoid = ff.upload(video_file_path, only_upload=True)

            if not uploaded:
                log(ident, f'Video not uploaded, skipping')

            log(ident, f'Uploaded Video with ID: {videoid}')
            ff.close()
            break
        except:
            log(ident, 'Video upload failed')
            stamp = str(now()).replace(".", "-")
            filepath = f'{folder}/error_{stamp}'
            ff.driver.save_screenshot(Path(filepath + '.png').abspath())

            with open(Path(filepath + '.html').abspath(), "w+") as f:
                f.write(ff.driver.find_element_by_xpath('//html').get_attribute('outerHTML'))

        ff.close()
        time.sleep(10)
        counter += 1

    return videoid
