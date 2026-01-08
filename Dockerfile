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

CMD ["python", "-m", "src.serve_and_ngrok"]