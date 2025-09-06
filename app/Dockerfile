FROM python:3.11-slim

WORKDIR /app

# System deps for numpy/scikit-learn
RUN apt-get update && apt-get install -y --no-install-recommends \ 
    build-essential     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY ../sql /app/sql
COPY ../scripts /app/scripts

# Create dirs for models/data
RUN mkdir -p /app/model /app/data

ENV PYTHONUNBUFFERED=1
