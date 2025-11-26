# SageMaker Training Container for Retail Prediction Model
FROM python:3.9-slim

# Set working directory
WORKDIR /opt/ml

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc6-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional ML libraries for training
RUN pip install --no-cache-dir \
    scikit-learn==1.3.0 \
    pandas==2.0.3 \
    numpy==1.24.3 \
    joblib==1.3.1 \
    boto3==1.28.17 \
    s3fs==2023.6.0

# Copy training scripts
COPY simple_training.py /opt/ml/code/train
COPY . /opt/ml/code/

# Set permissions
RUN chmod +x /opt/ml/code/train

# Environment variables for SageMaker
ENV SAGEMAKER_PROGRAM=simple_training.py
ENV PYTHONPATH=/opt/ml/code

# Create required SageMaker directories
RUN mkdir -p /opt/ml/input/data \
    /opt/ml/output \
    /opt/ml/model \
    /opt/ml/input/config

# Default command for SageMaker training
CMD ["python", "/opt/ml/code/simple_training.py"]