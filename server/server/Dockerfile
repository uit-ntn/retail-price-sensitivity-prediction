# Multi-stage build for FastAPI retail prediction API
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.9-slim

# Create non-root user for security
RUN groupadd -r apiuser && useradd -r -g apiuser apiuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/apiuser/.local

# Copy application code
COPY --chown=apiuser:apiuser . .

# Create directories for model and logs
RUN mkdir -p /tmp /app/logs && \
    chown -R apiuser:apiuser /tmp /app

# Switch to non-root user
USER apiuser

# Set Python path
ENV PATH=/home/apiuser/.local/bin:$PATH

# Environment variables
ENV PYTHONPATH=/app
ENV AWS_DEFAULT_REGION=ap-southeast-1
ENV MODEL_BUCKET=mlops-retail-forecast-models
ENV MODEL_KEY=models/retail-price-sensitivity/model.joblib

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python health_check.py || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
