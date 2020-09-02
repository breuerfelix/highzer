# highzer

Twitch Stream Analyzer

## Dependencies

- ffmpeg
- poetry

## Setup and Run

```bash
poetry install
poetry shell
python highzer/highzer.py --help
```

## Generate Google Credentials

Create a new Google API project and add the YouTube Data API.  
Create a file called `client_secrets.json` with the following content:
```json
{
  "web": {
    "client_id": "<client_id>",
    "client_secret": "<client_secret>",
    "redirect_uris": [],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}
```

Run the following:
```bash
python highzer/highzer.py login
```
This prompts you to login with your Google account. It creates a file called `oauth2.json` which stores an access and refresh token for your account.  
**Important:** If you want to run the application on a server, you need to copy those 2 files over!

## Nice to Know

[YouTube Channel](https://www.youtube.com/channel/UC0M8qvpFLG_QoimeBih_6nA)

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

## ToDo

- package this to pypi
