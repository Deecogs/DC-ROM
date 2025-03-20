# Use Python 3.10 slim as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create directory structure
RUN mkdir -p /app/api /app/rom /app/utils /app/static /app/templates

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ /app/api/
COPY rom/ /app/rom/
COPY utils/ /app/utils/
COPY static/ /app/static/
COPY templates/ /app/templates/
COPY *.py /app/

# Create symbolic links for demo scripts
RUN ln -sf /app/demo.py /usr/local/bin/demo && \
    ln -sf /app/holistic_demo.py /usr/local/bin/holistic-demo && \
    ln -sf /app/run.py /usr/local/bin/rom-run && \
    chmod +x /app/*.py

# Create a non-root user and change ownership
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Set up a health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]