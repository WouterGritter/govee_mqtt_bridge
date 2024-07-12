FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ARG IMAGE_VERSION=Unknown
ENV IMAGE_VERSION=${IMAGE_VERSION}

COPY *.py ./
CMD [ "python3", "-u", "main.py" ]
