FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:20231009.v1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src
CMD ["python", "src/train.py", "--data", "/mnt/data", "--out_dir", "/mnt/output"]
