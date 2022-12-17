# Build an image that can do training and inference in SageMaker
# This is a Python 3 image that uses the nginx, gunicorn, flask stack
# for serving inferences in a stable way.

FROM ubuntu:22.04


COPY requirements.txt /tmp/
RUN apt-get -y update && apt-get install -y --no-install-recommends \
        wget \
        python3-pip \
        python3-setuptools \
        ca-certificates \
        nginx \
        gcc \
        libpq-dev \
        python3-dev \
        python3-venv \
        python3-wheel \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/bin/python
RUN ln -sf /usr/bin/pip3 /usr/bin/pip

RUN pip install -r /tmp/requirements.txt

RUN ls
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

COPY ./src/app /app
COPY ./data /data