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
ENV MYSQL_HOST="None"
ENV MYSQL_DATABASE="None"
ENV MYSQL_USER="None"
ENV MYSQL_PASSWORD="None"

#Can add MYSQL_PORT for the port number

CMD [ "python3", "-u", "main.py" ]