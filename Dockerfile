# Build an image that can do training and inference in SageMaker
# This is a Python 3 image that uses the nginx, gunicorn, flask stack
# for serving inferences in a stable way.

FROM ubuntu:22.04


COPY requirements.txt /tmp/

RUN set -xe \
    && apt-get update \
    && apt-get install python3-pip
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

RUN ls
COPY ./app /app
COPY ./data /data