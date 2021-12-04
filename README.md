# highzer

Twitch Stream Analyzer and Video Cutter

## Dependencies

- poetry
- python
- ffmpeg
- imagemagick

__Recommended:__ Run your scripts in a container with the `Dockerfile` provided in this Repo.

## Setup and Run

```bash
poetry install
poetry shell
highzer --help
# or
nix-shell
highzer --help
```

## Nice to Know

[YouTube Channel](https://www.youtube.com/channel/UC0M8qvpFLG_QoimeBih_6nA) which i automate with this script.

```bash
# broadcast ID
export ID = ""

# download a broadcast
streamlink -o "output.ts" "https://www.twitch.tv/videos/$ID" best
# convert to mp4
ffmpeg -i output.ts -c copy output.mp4

# download chat
tcd --video $ID --output ~/code/twitch-analyzer --format json

# extract audio from mp4
ffmpeg -i output.mp4 -map 0:a sound.wav

# chunk wav files
ffmpeg -i raw.mp4 -map 0:a -segment_time 00:30:00 -f segment chunk%03d.wav
```

## ToDo

- package this to pypi
- schedule videos
- add videos to playlist
