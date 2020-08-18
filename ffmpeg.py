from utils import run


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


def merge(input_files, output_file):
    lines = [f"file '{file}'\n" for file in input_files]
    # TODO create this file in temp folder
    with open("chunk_list.txt", "w+") as file:
        file.writelines(lines)

    run(
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        "chunk_list.txt",
        "-c",
        "copy",
        output_file,
    )

    # TODO remove chunk list file
