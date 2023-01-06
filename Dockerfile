FROM python:3

RUN apt-get update && apt-get install -y ca-certificates --no-install-recommends

RUN mkdir /opt/demo
WORKDIR /opt/demo
COPY ./requirements.txt .

ENV PYTHONUNBUFFERED 1
COPY . .
