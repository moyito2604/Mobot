FROM python:3.12.3-alpine

# Adding Labels to identify repository for github
LABEL org.opencontainers.image.source=https://github.com/moyito2604/Mobot
LABEL org.opencontainers.image.description="Containerized Version of Mobot"
LABEL org.opencontainers.image.licenses=MIT

# copy requirements, upgrade pip and install requirements.
COPY /requirements.txt /requirements.txt
RUN apk update
RUN apk upgrade --available && sync
RUN apk add --no-cache ffmpeg
RUN apk add --no-cache build-base
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt

# Set work directory, copy source code to there
WORKDIR /app
COPY . .

# Set Arguments
ENV token="TOKEN"
# Bot Owner ID for administration
ENV ownerid="ID"
ENV dockerstatus=Yes
ENV MYSQL_HOST="None"
ENV MYSQL_DATABASE="None"
ENV MYSQL_USER="None"
ENV MYSQL_PASSWORD="None"

#Can add MYSQL_PORT for the port number

CMD [ "python3", "-u", "main.py" ]