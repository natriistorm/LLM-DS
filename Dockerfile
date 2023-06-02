# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

COPY . /src

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8030"]

EXPOSE 8030
