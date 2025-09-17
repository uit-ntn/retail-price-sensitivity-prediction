import os
from sagemaker import image_uris
from sagemaker.model import Model

role = os.getenv("SM_EXEC_ROLE_ARN")
region = os.getenv("AWS_REGION", "ap-southeast-1")
model_artifact = os.getenv("MODEL_ARTIFACT")
model_package_group_name = os.getenv("MODEL_PACKAGE_GROUP_NAME", "retail-mlops-group")

image_uri = image_uris.retrieve(framework="sklearn", region=region, version="1.2-1", py_version="py3", image_scope="inference")

model = Model(
    model_data=model_artifact,
    role=role,
    image_uri=image_uri,
    name="retail-mlops-model"
)

package = model.register(
    content_types=["text/csv", "application/json"],
    response_types=["application/json"],
    model_package_group_name=model_package_group_name,
    inference_instances=["ml.m5.large"],
    transform_instances=["ml.m5.large"]
)

print(f"MODEL_PACKAGE_ARN: {package.model_package_arn}")
