import os
import sagemaker
from sagemaker.model import ModelPackage

region = os.getenv("AWS_REGION", "ap-southeast-1")
session = sagemaker.Session()

model_package_arn = os.getenv("MODEL_PACKAGE_ARN")
endpoint_name = os.getenv("ENDPOINT_NAME", "retail-mlops-endpoint")

mp = ModelPackage(
    role=os.getenv("SM_EXEC_ROLE_ARN"),
    model_package_arn=model_package_arn,
    sagemaker_session=session
)

predictor = mp.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    endpoint_name=endpoint_name
)

print(f"DEPLOYED_ENDPOINT: {endpoint_name}")
