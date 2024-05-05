FROM python:3.9.19-alpine
ENV PYTHONBUFFERED 1
WORKDIR /main-service
COPY requirements.txt requirements.txt
RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev && pip3 install -r requirements.txt
RUN apk add --upgrade apache2-utils
COPY . .