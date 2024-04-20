# pull official base image
FROM python:3.11.3-slim-buster

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# initialize and migrate database (if applicable)
RUN flask db init && flask db migrate && flask db upgrade

# expose port
EXPOSE 5000

# command to run the application
CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api.app:app" ]
