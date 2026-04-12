FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ="Asia/Kolkata"
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg mediainfo && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["bash", "run.sh"]
