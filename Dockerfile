#FROM python:3-alpine
FROM python:3-slim-buster

LABEL org.opencontainers.image.source https://github.com/SENERGY-Platform/senergy-connector

#RUN apk --no-cache add git
RUN apt-get update && apt-get install -y git

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir .data

CMD [ "python", "-u", "./client.py"]
