import os
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.inputs import TrainingInput

region = os.getenv("AWS_REGION", "ap-southeast-1")
role = os.getenv("SM_EXEC_ROLE_ARN")
session = sagemaker.Session()

bucket = os.getenv("S3_DATA_BUCKET")
train_s3 = f"s3://{bucket}/train.csv"

estimator = SKLearn(
    entry_point="core/src/train.py",
    role=role,
    instance_type="ml.m5.large",
    framework_version="1.2-1",
    py_version="py3",
    source_dir="core/src",
    instance_count=1,
    base_job_name="retail-train"
)

estimator.fit({"train": TrainingInput(train_s3)})
print(f"MODEL_ARTIFACT: {estimator.model_data}")
