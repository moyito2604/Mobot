FROM python:3.10-slim-buster

# copy requirements, upgrade pip and install requirements.
COPY /requirements.txt /requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install ffmpeg

# Set work directory, copy source code to there
WORKDIR /app
COPY . .
