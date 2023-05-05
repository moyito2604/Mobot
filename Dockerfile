FROM python:3.10.11-alpine3.17

# copy requirements, upgrade pip and install requirements.
COPY /requirements.txt /requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt
RUN apk update
RUN apk upgrade --available && sync
RUN apk add --no-cache ffmpeg

# Set work directory, copy source code to there
WORKDIR /app
COPY . .

# Set Arguments
ENV token="TOKEN"
ENV dockerstatus=Yes

CMD [ "python3", "main.py" ]