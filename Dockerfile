# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

COPY . /src

CMD gunicorn --workers=1 server:app -b 0.0.0.0:8030 --timeout=1200

EXPOSE 8030
