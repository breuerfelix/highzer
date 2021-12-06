from datetime import date
from .utils import pretty_short_time


def get_yt_snippet(clips, category, period, n):
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
    tags.append(category.replace(" ", "").lower())
    tags.append("twitch")
    tags.append("highlight")
    tags.append(f"{period}{n}")

    # those chars throw errors with the youtube API
    invalid_chars = "<>"
    for char in invalid_chars:
        description = description.replace(char, "")

    return dict(
        title=f"{period.capitalize()} {n} - {category} - Top {len(clips)} Twitch Highlights {year}",
        description=description,
        tags=tags,
    )
