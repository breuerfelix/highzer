import os
import click
import requests
import schedule as sched
import time
from utils import run, pprint, locate_folder, get_week, retry
from chat import analyze_chat
from audio import analyze_audio, analyze_audio_test
from fpeg import cut, merge
from clip import cut_clips
from yt import save_video


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


@cli.command()
@click.argument("ident")
@click.option("-c", "--chunk-size", default=30, help="in seconds", show_default=True)
def analyze(ident, chunk_size=30):
    folder = locate_folder(ident)
    # analyze_chat(ident, chunk_size)

    highlights = analyze_audio(ident, chunk_size)

    files = []
    for index, high in enumerate(highlights):
        out_file = f"{folder}/chunk{index:03d}.mp4"
        files.append(out_file)
        cut(
            f"{folder}/raw.mp4",
            out_file,
            high["from"] - 5,
            high["length"] + chunk_size + 5,
        )

    merge(files, f"{folder}/highlight.mp4")

    for chunk in files:
        os.remove(chunk)


@cli.command()
@click.argument("ident")
@click.option(
    "-p", "--period", default="week", help="day / week / month / all", show_default=True
)
@click.option("-g", "--game", default=None)
@click.option("-c", "--channel", default=None)
def clip(ident, period, game, channel):
    if game is None and channel is None:
        print("Please provide a channel or a game!")
        return

    print("Clipping video...")
    clips, merged = cut_clips(ident, period, game, channel)
    save_video(ident, merged, clips, game or channel)


@cli.command()
def schedule():
    @retry
    def do_clip(game):
        week = get_week()
        pg = game.replace(" ", "").lower()
        ident = f"{week}_{pg}"

        clips, merged = cut_clips(ident, "week", game, None)
        save_video(ident, merged, clips, game)
        print(f"uploaded video: {ident}")

    upload_time = "12:00"
    sched.every().monday.at(upload_time).do(do_clip, game="Minecraft")
    sched.every().tuesday.at(upload_time).do(do_clip, game="World of Warcraft")
    sched.every().wednesday.at(upload_time).do(do_clip, game="Dota 2")
    sched.every().thursday.at(upload_time).do(do_clip, game="VALORANT")
    sched.every().friday.at(upload_time).do(
        do_clip, game="Counter Strike: Global Offensive"
    )
    sched.every().saturday.at(upload_time).do(do_clip, game="Fortnite")
    sched.every().sunday.at(upload_time).do(do_clip, game="League of Legends")

    while True:
        sched.run_pending()
        time.sleep(1)


@cli.command()
def test():
    print("imports working")
    return


if __name__ == "__main__":
    #clip('testing', 'week', 'leagueoflegends', None)
    cli()
