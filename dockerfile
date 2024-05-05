FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH /apps:$PYTHONPATH

COPY ./apps /apps
COPY ./requirements /apps/requirements

WORKDIR /apps

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y pkg-config libmariadb-dev-compat libmariadb-dev build-essential libpq-dev python3-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r /apps/requirements/requirements.txt && \
    apt-get clean -y

# Expose port
EXPOSE 80
