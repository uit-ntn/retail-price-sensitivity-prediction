# AWS Scripts - Retail Forecast MLOps

Thư mục này chứa tất cả **automation scripts** cho **SageMaker MLOps pipeline**, **container management**, và **monitoring** trên Amazon Web Services.

---

## 📁 Cấu trúc thư mục

```
script/
├── pipelines/                    # SageMaker Pipelines
│   ├── sagemaker_pipeline.py    # Main ML pipeline definition
│   └── params.json              # Pipeline parameters
│
├── monitoring/                   # Model monitoring scripts
│   ├── data_quality_baseline.py       # Data quality baseline creation
│   ├── schedule_data_quality_monitor.py  # Data quality monitoring
│   └── schedule_model_quality_monitor.py # Model quality monitoring
│
├── create_training_job.py        # SageMaker training job creation
├── register_model.py            # Model registry management
├── deploy_endpoint.py           # SageMaker endpoint deployment
├── autoscaling_endpoint.py      # Endpoint auto-scaling configuration
├── processing_evaluate.py       # Model evaluation processing
├── ecr_build_push.sh            # Container build and push script
└── README.MD                    # File này
```

---

## 🚀 Core SageMaker Scripts

### `create_training_job.py`
**SageMaker Training Job** creation script:

**Chức năng:**
- Tạo và submit training job lên SageMaker
- Configure training parameters và resources
- Monitor job status và output artifacts

**Usage:**
```bash
# Set environment variables
export S3_DATA_BUCKET="retail-mlops-data-123456-ap-southeast-1"
export SM_EXEC_ROLE_ARN="arn:aws:iam::123456:role/sagemaker-exec-role"

# Run training job
python create_training_job.py
```

**Environment Variables:**
- `S3_DATA_BUCKET` - S3 bucket chứa training data
- `SM_EXEC_ROLE_ARN` - SageMaker execution role ARN
- `MODEL_PACKAGE_GROUP_NAME` - Model package group name

### `register_model.py`
**Model Registry** management script:

**Chức năng:**
- Đăng ký trained model vào SageMaker Model Registry
- Set model metadata và approval status
- Create model package với versioning

**Usage:**
```bash
# Set model artifact path (từ training job output)
export MODEL_ARTIFACT="s3://bucket/path/to/model.tar.gz"

# Register model
python register_model.py
```

**Features:**
- Model versioning tự động
- Metadata tracking (accuracy, metrics)
- Approval workflow integration
- Model lineage tracking

### `deploy_endpoint.py`
**SageMaker Endpoint** deployment script:

**Chức năng:**
- Deploy model từ registry thành inference endpoint
- Configure endpoint instance type và scaling
- Setup endpoint monitoring

**Usage:**
```bash
# Set model package ARN (từ register_model.py output)
export MODEL_PACKAGE_ARN="arn:aws:sagemaker:region:account:model-package/..."

# Deploy endpoint
python deploy_endpoint.py
```

**Configuration:**
- **Instance Type:** ml.t2.medium (configurable)
- **Initial Instance Count:** 1
- **Auto Scaling:** Enabled (via autoscaling_endpoint.py)

### `autoscaling_endpoint.py`
**Endpoint Auto-scaling** configuration:

**Chức năng:**
- Setup Application Auto Scaling cho SageMaker endpoint
- Configure scaling policies dựa trên metrics
- Set min/max instance limits

**Usage:**
```bash
# Set endpoint name
export ENDPOINT_NAME="retail-mlops-endpoint"

# Configure auto-scaling
python autoscaling_endpoint.py
```

**Scaling Configuration:**
- **Min Capacity:** 1 instance
- **Max Capacity:** 10 instances
- **Target Metric:** InvocationsPerInstance
- **Target Value:** 100 invocations/minute

### `processing_evaluate.py`
**Model Evaluation** processing job:

**Chức năng:**
- Chạy model evaluation trên SageMaker Processing
- Generate model metrics và reports
- Compare với baseline models

**Usage:**
```bash
# Set evaluation parameters
export MODEL_PATH="s3://bucket/model/model.tar.gz"
export TEST_DATA_PATH="s3://bucket/test/test.csv"

# Run evaluation
python processing_evaluate.py
```

**Outputs:**
- Model accuracy metrics
- Confusion matrix
- Feature importance
- Performance reports

---

## 📦 Container Management

### `ecr_build_push.sh`
**Docker build và push** script cho ECR:

**Chức năng:**
- Build Docker image từ server code
- Authenticate với ECR
- Push image với git commit tag

**Usage:**
```bash
# Basic usage (sử dụng git commit hash làm tag)
./ecr_build_push.sh ECR_REPO_URI

# Custom tag
./ecr_build_push.sh ECR_REPO_URI custom-tag

# Custom context directory
./ecr_build_push.sh ECR_REPO_URI latest ../../server
```

**Parameters:**
- `$1` - ECR repository URI
- `$2` - Image tag (default: git commit hash)
- `$3` - Build context directory (default: ../../server)

**Example:**
```bash
# Set environment
export AWS_REGION="ap-southeast-1"

# Build and push
./ecr_build_push.sh \
  123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/retail-forecast-server \
  v1.0.0 \
  ../../server
```

**Features:**
- Automatic ECR authentication
- Git-based tagging
- Build context flexibility
- Error handling với set -euo pipefail

---

## 🔄 SageMaker Pipelines (`pipelines/`)

### `sagemaker_pipeline.py`
**Complete ML Pipeline** definition:

#### Pipeline Components:

### 1. **Parameters**
```python
project = ParameterString(name="ProjectName", default_value="retail-forecast")
data_bucket = ParameterString(name="S3DataBucket", default_value="REPLACE_ME-data")
artifacts_bucket = ParameterString(name="S3ArtifactsBucket", default_value="REPLACE_ME-artifacts")
training_image = ParameterString(name="TrainingImageUri", default_value="...")
instance_type = ParameterString(name="InstanceType", default_value="ml.m5.xlarge")
```

### 2. **Training Step**
```python
estimator = SKLearn(
    entry_point="train.py",
    role=role,
    framework_version="1.2-1",
    instance_type=instance_type,
    instance_count=instance_count,
    output_path=f"s3://{artifacts_bucket}/models"
)
```

### 3. **Evaluation Step**
- Model performance evaluation
- Metrics generation
- Quality gates

### 4. **Model Registration Step**
- Conditional model registration
- Approval workflow
- Versioning management

### 5. **Cache Configuration**
```python
cache = CacheConfig(enable_caching=True, expire_after="30d")
```

**Benefits:**
- Step-level caching
- Parallel execution
- Conditional steps
- Parameter flexibility

### `params.json`
**Pipeline parameters** configuration:
```json
{
  "ProjectName": "retail-forecast",
  "S3DataBucket": "retail-mlops-data-123456-ap-southeast-1",
  "S3ArtifactsBucket": "retail-mlops-artifacts-123456-ap-southeast-1",
  "InstanceType": "ml.m5.xlarge",
  "ModelPackageGroupName": "retail-forecast",
  "ModelApprovalStatus": "PendingManualApproval"
}
```

**Usage:**
```bash
# Execute pipeline with custom parameters
python sagemaker_pipeline.py --config params.json

# Override specific parameters
python sagemaker_pipeline.py \
  --project-name "retail-forecast-prod" \
  --instance-type "ml.m5.2xlarge"
```

---

## 📊 Model Monitoring (`monitoring/`)

### `data_quality_baseline.py`
**Data Quality Baseline** creation:

**Chức năng:**
- Analyze training dataset characteristics
- Create statistical baselines
- Generate data quality constraints

**Usage:**
```bash
# Set baseline parameters
export BASELINE_DATA_PATH="s3://bucket/train/baseline.csv"
export BASELINE_OUTPUT_PATH="s3://bucket/baselines/data-quality"

# Create baseline
python monitoring/data_quality_baseline.py
```

**Outputs:**
- Statistical constraints
- Data schema validation
- Baseline statistics

### `schedule_data_quality_monitor.py`
**Data Quality Monitoring** scheduler:

**Chức năng:**
- Setup continuous data quality monitoring
- Compare incoming data với baseline
- Alert on data drift detection

**Configuration:**
- **Schedule:** Hourly/Daily monitoring
- **Baseline:** Statistical constraints
- **Thresholds:** Configurable drift detection

### `schedule_model_quality_monitor.py`
**Model Quality Monitoring** scheduler:

**Chức năng:**
- Monitor model performance metrics
- Detect model drift và degradation
- Trigger retraining workflows

**Metrics:**
- Prediction accuracy
- Feature importance changes
- Data distribution shifts
- Performance degradation

**Usage:**
```bash
# Setup model monitoring
export ENDPOINT_NAME="retail-mlops-endpoint"
export BASELINE_MODEL_PATH="s3://bucket/baselines/model"

# Schedule monitoring
python monitoring/schedule_model_quality_monitor.py
```

---

## 🚀 Deployment Workflows

### 1. **Complete Training Pipeline**
```bash
#!/bin/bash
set -e

# Step 1: Create training job
echo "Starting training job..."
python create_training_job.py | tee train.log

# Step 2: Extract model artifact
MODEL_ARTIFACT=$(grep "MODEL_ARTIFACT" train.log | cut -d" " -f2)
export MODEL_ARTIFACT

# Step 3: Register model
echo "Registering model: $MODEL_ARTIFACT"
python register_model.py | tee register.log

# Step 4: Extract model package ARN
MODEL_PACKAGE_ARN=$(grep "MODEL_PACKAGE_ARN" register.log | cut -d" " -f2)
export MODEL_PACKAGE_ARN

# Step 5: Deploy endpoint
echo "Deploying endpoint: $MODEL_PACKAGE_ARN"
python deploy_endpoint.py

# Step 6: Configure auto-scaling
echo "Configuring auto-scaling..."
python autoscaling_endpoint.py

echo "Pipeline completed successfully!"
```

### 2. **Container Build & Deploy**
```bash
#!/bin/bash
set -e

# Build and push container
./ecr_build_push.sh \
  $ECR_REPO_URI \
  $(git rev-parse --short HEAD) \
  ../../server

# Update Kubernetes deployment
kubectl set image deployment/retail-server \
  retail-server=$ECR_REPO_URI:$(git rev-parse --short HEAD) \
  -n retail

# Wait for rollout
kubectl rollout status deployment/retail-server -n retail
```

### 3. **SageMaker Pipeline Execution**
```bash
#!/bin/bash
set -e

# Update pipeline parameters
python -c "
import json
params = json.load(open('pipelines/params.json'))
params['S3DataBucket'] = '$S3_DATA_BUCKET'
params['S3ArtifactsBucket'] = '$S3_ARTIFACTS_BUCKET'
json.dump(params, open('pipelines/params.json', 'w'), indent=2)
"

# Execute pipeline
python pipelines/sagemaker_pipeline.py

echo "SageMaker pipeline submitted successfully!"
```

---

## 🔧 Configuration Management

### Environment Variables:

#### Required:
```bash
# AWS Configuration
export AWS_REGION="ap-southeast-1"
export AWS_ACCOUNT_ID="123456789012"

# SageMaker Configuration
export SM_EXEC_ROLE_ARN="arn:aws:iam::123456:role/sagemaker-exec-role"
export S3_DATA_BUCKET="retail-mlops-data-123456-ap-southeast-1"
export S3_ARTIFACTS_BUCKET="retail-mlops-artifacts-123456-ap-southeast-1"

# Model Configuration
export MODEL_PACKAGE_GROUP_NAME="retail-forecast"
export ENDPOINT_NAME="retail-mlops-endpoint"
```

#### Optional:
```bash
# Training Configuration
export TRAIN_ENTRYPOINT="train.py"
export INSTANCE_TYPE="ml.m5.xlarge"
export INSTANCE_COUNT="1"

# Container Configuration
export ECR_REPO_URI="123456.dkr.ecr.ap-southeast-1.amazonaws.com/retail-forecast"

# Monitoring Configuration
export ENABLE_DATA_QUALITY_MONITORING="true"
export ENABLE_MODEL_QUALITY_MONITORING="true"
```

---

## 📊 Monitoring & Logging

### Script Execution Logs:
```bash
# Training job logs
python create_training_job.py 2>&1 | tee logs/training-$(date +%Y%m%d-%H%M%S).log

# Pipeline execution logs
python pipelines/sagemaker_pipeline.py 2>&1 | tee logs/pipeline-$(date +%Y%m%d-%H%M%S).log
```

### SageMaker Job Monitoring:
```bash
# Check training job status
aws sagemaker describe-training-job --training-job-name retail-forecast-train-$(date +%Y%m%d-%H%M%S)

# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name retail-mlops-endpoint

# Check pipeline execution
aws sagemaker list-pipeline-executions --pipeline-name retail-forecast-pipeline
```

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. **Training Job Failures**
```bash
# Check training job logs
aws logs describe-log-streams --log-group-name /aws/sagemaker/TrainingJobs

# Get specific job logs
aws logs get-log-events --log-group-name /aws/sagemaker/TrainingJobs --log-stream-name training-job-name/algo-1-timestamp
```

#### 2. **Endpoint Deployment Issues**
```bash
# Check endpoint configuration
aws sagemaker describe-endpoint-config --endpoint-config-name retail-mlops-config

# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name retail-mlops-endpoint

# Test endpoint
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name retail-mlops-endpoint \
  --content-type application/json \
  --body '{"instances": [[1,2,3,4]]}' \
  output.json
```

#### 3. **ECR Push Failures**
```bash
# Check ECR authentication
aws ecr get-login-password --region ap-southeast-1

# Check repository exists
aws ecr describe-repositories --repository-names retail-forecast-server

# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456:user/username \
  --action-names ecr:BatchGetImage ecr:GetDownloadUrlForLayer
```

#### 4. **Pipeline Execution Failures**
```bash
# Check pipeline definition
aws sagemaker describe-pipeline --pipeline-name retail-forecast-pipeline

# Check execution details
aws sagemaker describe-pipeline-execution --pipeline-execution-arn arn:aws:sagemaker:...

# List failed steps
aws sagemaker list-pipeline-execution-steps --pipeline-execution-arn arn:aws:sagemaker:...
```

---

## 💰 Cost Optimization

### Training Optimization:
```bash
# Use Spot instances for training
export INSTANCE_TYPE="ml.m5.xlarge"
export USE_SPOT_INSTANCES="true"

# Optimize instance selection
python -c "
import sagemaker
print('Recommended instance types:')
print('- ml.m5.large (2 vCPU, 8GB RAM) - Small datasets')
print('- ml.m5.xlarge (4 vCPU, 16GB RAM) - Medium datasets')
print('- ml.m5.2xlarge (8 vCPU, 32GB RAM) - Large datasets')
"
```

### Endpoint Optimization:
```bash
# Use smaller instances for inference
export INFERENCE_INSTANCE_TYPE="ml.t2.medium"

# Setup auto-scaling to scale to zero
python autoscaling_endpoint.py --min-capacity 0 --max-capacity 5
```

---

## 📚 Tài liệu tham khảo

- [Amazon SageMaker Developer Guide](https://docs.aws.amazon.com/sagemaker/)
- [SageMaker Python SDK](https://sagemaker.readthedocs.io/)
- [SageMaker Pipelines](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines.html)
- [SageMaker Model Registry](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html)
- [SageMaker Model Monitor](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html)
- [Amazon ECR User Guide](https://docs.aws.amazon.com/ecr/)
