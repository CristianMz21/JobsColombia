FROM python:3.11-slim

LABEL maintainer="TechJobs Colombia"
LABEL description="Web scraper for tech job listings in Colombia"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN mkdir -p /app/logs

CMD ["python", "main.py"]
