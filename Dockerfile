# ------------------------------------------------------------------------------------------------------- #
# Dockerfile to inspect project directory structure on container start
# ------------------------------------------------------------------------------------------------------- #
# MAKE-AI-GREAT-AGAIN: https://www.facebook.com/share/r/1EYTDiZk5H/

# Stage 1: Base build stage, add python ~ Python Management
FROM python:3.12-slim AS builder

# Set Python environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies to connect python with sql databases
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /super-neat-python-project
COPY ./ /super-neat-python-project
WORKDIR /super-neat-python-project

# install python requirements
RUN python -m pip install --upgrade pip
# RUN pip install -r requirements.txt

CMD ["launch.sh"]