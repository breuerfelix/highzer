FROM python:3.11-slim-buster

WORKDIR /usr/app

# set timezone
RUN echo "Europe/Berlin" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

# dependencies for moviepy
RUN apt-get update && \
  apt-get install -y --no-install-recommends --no-install-suggests \
  ffmpeg imagemagick fonts-liberation

RUN apt-get install -y locales && \
  locale-gen C.UTF-8 && \
  /usr/sbin/update-locale LANG=C.UTF-8

# modify ImageMagick policy file so that Textclips work correctly.
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml
ENV LC_ALL C.UTF-8

COPY pyproject.toml .
COPY highzer highzer

# install dependencies for python
RUN pip install .

# otherwhise logs will not get printed to docker logs
ENV PYTHONUNBUFFERED=1

CMD ["highzer", "schedule"]
