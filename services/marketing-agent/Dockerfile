FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt
RUN pip install --no-binary=:all: tensorflow numpy

COPY . ./

EXPOSE 8002 5055

# Entrypoint runs both Rasa server and action server
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
