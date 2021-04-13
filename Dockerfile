FROM python:3-alpine

LABEL org.opencontainers.image.source https://github.com/SENERGY-Platform/senergy-connector

RUN apk --no-cache add git

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir sc_data

CMD [ "python", "-u", "./client.py"]
