FROM python:3.8-slim-buster

WORKDIR /usr/app

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

# dependencies for selenium
RUN apt-get install -y --no-install-recommends --no-install-suggests \
  wget bzip2 libgtk-3-0 libdbus-glib-1-2 libx11-xcb1 libxt6 && \
  wget -q -O - "https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64" | tar -xj -C /opt && \
  ln -s /opt/firefox/firefox /usr/local/bin/ && \
  export GECKO_DRIVER_VERSION='v0.29.0' && \
  wget https://github.com/mozilla/geckodriver/releases/download/$GECKO_DRIVER_VERSION/geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz && \
  tar -xvzf geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz && \
  rm geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz && \
  chmod +x geckodriver && \
  cp geckodriver /usr/local/bin/

# installing python dependencies
RUN apt-get install -y --no-install-recommends --no-install-suggests \
  git

# install dependencies for python
COPY pyproject.toml .
RUN pip install .

COPY highzer highzer

# otherwhise logs will not get printed to docker logs
ENV PYTHONUNBUFFERED=1

CMD ["highzer", "schedule"]
