# 1. Base image
FROM python:3.11-slim

# 2. OS packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 && \
    rm -rf /var/lib/apt/lists/*

# 3. Working directory
WORKDIR /app

# 4. Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

## .env file is NOT copied into the image for security. Pass it at runtime with --env-file or Docker Compose.

# 6. App code
COPY . .

# 7. Default command
CMD ["streamlit", "run", "Home.py", \
     "--server.headless=true", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
