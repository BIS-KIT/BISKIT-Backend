FROM amd64/python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

COPY ./apps /apps
COPY ./requirements /apps/requirements

WORKDIR /apps

# Install dependencies
RUN python -m venv /py && \
    . /py/bin/activate && \ 
    /py/bin/pip install --upgrade pip && \
    apt-get clean -y && \
    apt-get clean -y && \
    apt-get update -y && \
    apt-get install -y pkg-config libmariadb-dev-compat libmariadb-dev build-essential libpq-dev python3-dev && \
    /py/bin/pip install -r /apps/requirements/requirements.txt

# Expose port
EXPOSE 8000
