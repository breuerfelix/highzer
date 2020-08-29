FROM python:3-slim

WORKDIR /usr/app

RUN apt-get update \
  && apt-get install -y --no-install-recommends ffmpeg
RUN pip install poetry

COPY pyproject.toml .
RUN poetry lock && poetry export -f requirements.txt > requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-u", "highzer/highzer.py", "schedule"]
