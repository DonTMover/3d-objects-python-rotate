FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt .
COPY /src /app
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	libgl1-mesa-glx \
	libosmesa6 \
	libxrender1 \
	libxext6 \
	libx11-6 \
	xvfb \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Default to running the bot; docker-compose overrides commands for web/frontend as needed
CMD ["python", "-m", "src.bot"]

# Healthcheck: verify web service status endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD curl -f http://localhost:8000/status || exit 1