FROM python:3-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends ffmpeg

WORKDIR /usr/app

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "-u", "cli.py", "schedule"]
