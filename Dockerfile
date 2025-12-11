# Dockerfile for IHRAS v1.0 Streamlit app
FROM python:3.10-slim

# Avoid buffering Python output
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (if any for scipy/poliastr etc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy code
COPY . /app

# Install pip dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Default envs for Streamlit
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV PYTHONPATH=/app

# Entrypoint
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
