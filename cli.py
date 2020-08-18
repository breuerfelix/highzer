import os
import click
import requests
from utils import run, pprint, locate_folder
from chat import analyze_chat
from audio import analyze_audio, analyze_audio_test
from ffmpeg import cut, merge


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
def test():
    highlights = analyze_audio_test(1)
    pprint(highlights)


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


if __name__ == "__main__":
    cli()
