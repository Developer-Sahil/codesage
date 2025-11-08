# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including git
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn flask-cors

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p refactored_codebase temp_repo

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the web application with gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 3600 web_app:app