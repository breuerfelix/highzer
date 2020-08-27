# highzer

## how to
```bash
# ffmpeg required
poetry install # not working ??
pip install -r requirements.txt # working!
python cli.py --help
```

## nice to know

[youtube channel](https://www.youtube.com/channel/UC0M8qvpFLG_QoimeBih_6nA)

```bash
export ID = ""
# download stream
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
