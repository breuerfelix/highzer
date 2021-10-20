import os
import click
import schedule as sched
import time
from .utils import locate_folder, get_week, get_day
from .clip import fetch_clip_data, merge_clips, do_clips
from .yt import upload_video


GAMES = [
    "New World",
    "Just Chatting",
    "Minecraft",
    "World of Warcraft",
    "Dota 2",
    "VALORANT",
    "Counter Strike: Global Offensive",
    "Fortnite",
    "League of Legends",
    "Guild Wars 2",
]


@click.group()
def cli():
    pass


@cli.command()
@click.argument("ident")
@click.option("-c", "--chunk-size", default=30, help="in seconds", show_default=True)
def analyze(ident, chunk_size=30):
    folder = locate_folder(ident)
    highlights = []
    # highlights = analyze_chat(ident, chunk_size)
    # highlights = analyze_audio(ident, chunk_size)

    files = []
    for index, high in enumerate(highlights):
        out_file = f"{folder}/chunk{index:03d}.mp4"
        files.append(out_file)
        # TODO rewrite with moviepy
        # cut(
            # f"{folder}/raw.mp4",
            # out_file,
            # high["from"] - 5,
            # high["length"] + chunk_size + 5,
        # )

    # merge(files, f"{folder}/highlight.mp4")

    for chunk in files:
        os.remove(chunk)


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

    fetch_clip_data(ident, period, game, channel)
    merge_clips(ident)
    if upload:
        upload_video(ident)

    print(f"Finished video {ident}")


@cli.command()
def schedule():
    print("starting schedule")


    def weekly():
        do_clips(GAMES, "week", get_week(), 20)

    def daily():
        do_clips(GAMES, "day", get_day(), 5)

    # def monthly():
        # do_clips(GAMES, "month", get_month(), 50, 15)

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
    do_clips(GAMES, period, get_day(), 5)


@cli.command()
def test():
    print("imports working")


if __name__ == "__main__":
    cli()
