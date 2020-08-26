from utils import run
import os


def cat(input_files, output_file):
    run(
        "cat", *input_files, ">", output_file,
    )


def cut(input_file, output_file, start, duration):
    run(
        "ffmpeg",
        "-i",
        input_file,
        "-ss",
        start,
        "-t",
        duration,
        "-c",
        "copy",
        output_file,
    )


def concat(input_files, output_file, temp_folder):
    temp_folder = os.path.abspath(temp_folder)

    if os.path.exists(temp_folder):
        os.remove(temp_folder)

    os.makedirs(temp_folder)

    run(
        "node_modules/.bin/ffmpeg-concat",
        "-O",
        temp_folder,
        "-c",
        5,
        "-d",
        1500,
        "-o",
        output_file,
        *input_files,
    )


def concat_fast(input_files, output_file):
    joined = "|".join(input_files)
    files = f'concat:"{joined}"'
    run(
        "ffmpeg", "-i", files, "-c", "copy", output_file,
    )


def sample(input_file):
    split = input_file.split(".")
    split[-2] = f"{split[-2]}-temp"
    temp_file = ".".join(split)

    os.rename(input_file, temp_file)

    run(
        "ffmpeg",
        "-i",
        temp_file,
        "-filter_complex",
        "[0:v]scale=1920x1080[Scaled]",
        "-map",
        "[Scaled]",
        input_file,
    )

    """
    run(
        "ffmpeg",
        "-i",
        temp_file,
        "-c",
        "copy",
        "-s",
        "1920x1080",
        "-r",
        60,
        input_file,
    )
    """

    os.remove(temp_file)


def convert(input_file, output_file):
    run(
        "ffmpeg", "-i", input_file, output_file,
    )

    os.remove(input_file)


def merge(input_files, output_file):
    lines = [f"file '{file}'\n" for file in input_files]
    chunk_file = "chunk_list.txt"

    with open(chunk_file, "w+") as file:
        file.writelines(lines)

    run(
        "ffmpeg",
        # "-fflags",
        # "+igndts",
        "-f",
        "concat",
        "-i",
        chunk_file,
        "-safe",
        "0",
        "-c",
        "copy",
        output_file,
    )

    os.remove(chunk_file)
