FROM python:3-slim

WORKDIR /usr/app

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  ffmpeg imagemagick fonts-liberation


RUN apt-get install -y locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8

ENV LC_ALL C.UTF-8

RUN pip install poetry

COPY pyproject.toml .
RUN poetry lock && poetry export -f requirements.txt > requirements.txt
RUN pip install -r requirements.txt

# modify ImageMagick policy file so that Textclips work correctly.
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml

COPY . .

CMD ["python3", "-u", "highzer/highzer.py", "schedule"]
