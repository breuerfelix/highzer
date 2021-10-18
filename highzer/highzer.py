import os
import click
#import requests
import schedule as sched
import time
from .utils import run, locate_folder, get_week, get_day
#from .chat import analyze_chat
#from .audio import analyze_audio, analyze_audio_test
#from .fpeg import cut, merge
from .clip import get_clips, cut_clips, do_clips
from .yt import save_video, upload_video


@click.group()
def cli():
    pass


@cli.command()
@click.argument("ident")
@click.argument("url")
def fetch(ident, url):
    folder = locate_folder(ident)

    # create user folder
    if not os.path.exists(folder):
        os.makedirs(folder)

    id = url.split("/")[-1]
    print(f"ID: {id}")

    # download chat
    run(
        "tcd", "--video", id, "--output", ident, "--format", "json",
    )
    os.rename(f"{folder}/{id}.json", f"{folder}/chat.json")

    # download VOD
    run(
        "streamlink", "-o", f"{folder}/raw.ts", f"{url}", "best",
    )


@cli.command()
@click.argument("ident")
def convert(ident):
    folder = locate_folder(ident)

    # convert to mp4
    run(
        "ffmpeg", "-i", f"{folder}/raw.ts", "-c", "copy", f"{folder}/raw.mp4",
    )

    # remove old .ts format to save storage
    os.remove(f"{folder}/raw.ts")

    # extract sound
    # run("ffmpeg", "-i", f"{folder}/raw.mp4", "-map", "0:a", f"{folder}/sound.mp3")


# @cli.command()
# @click.argument("ident")
# @click.option("-c", "--chunk-size", default=30, help="in seconds", show_default=True)
# def analyze(ident, chunk_size=30):
    # folder = locate_folder(ident)
    # # analyze_chat(ident, chunk_size)

    # highlights = analyze_audio(ident, chunk_size)

    # files = []
    # for index, high in enumerate(highlights):
        # out_file = f"{folder}/chunk{index:03d}.mp4"
        # files.append(out_file)
        # cut(
            # f"{folder}/raw.mp4",
            # out_file,
            # high["from"] - 5,
            # high["length"] + chunk_size + 5,
        # )

    # merge(files, f"{folder}/highlight.mp4")

    # for chunk in files:
        # os.remove(chunk)


@cli.command()
@click.argument("ident")
@click.option(
    "-p", "--period", default="week", help="day / week / month / all", show_default=True
)
@click.option("-g", "--game", default=None)
@click.option("-c", "--channel", default=None)
@click.option("-u", "--upload", is_flag=True)
def clip(ident, period, game, channel, upload):
    if game is None and channel is None:
        print("Please provide a channel or a game!")
        return

    print(f"Clipping video {ident}")

    get_clips(ident, period, game, channel)
    cut_clips(ident)
    save_video(ident)
    if upload:
        upload_video(ident)

    print(f"Finished video {ident}")


@cli.command()
def schedule():
    print("starting schedule")

    games = [
        "Minecraft",
        "World of Warcraft",
        "Dota 2",
        "VALORANT",
        "Counter Strike: Global Offensive",
        "Fortnite",
        "League of Legends",
        "Guild Wars 2",
    ]

    def weekly():
        do_clips(games, "week", get_week(), 20)

    def daily():
        do_clips(games, "day", get_day(), 5)

    # def monthly():
        # do_clips(games, "month", get_month(), 50, 15)

    sched.every().saturday.at("12:00").do(weekly)
    sched.every().day.at("23:00").do(daily)

    while True:
        sched.run_pending()
        time.sleep(10)


@cli.command()
@click.option(
    "-p", "--period", default="week", help="day / week / month / all", show_default=True
)
def manual(period):
    games = [
        "Minecraft",
        "World of Warcraft",
        "Dota 2",
        "VALORANT",
        "Counter Strike: Global Offensive",
        "Fortnite",
        "League of Legends",
        "Guild Wars 2",
    ]

    do_clips(games, period, get_day(), 5)


@cli.command()
def test():
    print("imports working")


if __name__ == "__main__":
    cli()
