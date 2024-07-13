FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY *.py ./

ARG IMAGE_VERSION=Unknown
ENV IMAGE_VERSION=${IMAGE_VERSION}

CMD [ "python3", "-u", "main.py" ]
