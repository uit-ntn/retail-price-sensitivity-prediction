import json, os, time
import boto3
import sagemaker
from sagemaker.workflow.parameters import ParameterString, ParameterInteger
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import CacheConfig
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from sagemaker.workflow.steps import TrainingStep, ProcessingStep
from sagemaker.workflow.model_step import ModelStep
from sagemaker.model_metrics import MetricsSource, ModelMetrics
from sagemaker import get_execution_role

session = sagemaker.Session()
region = session.boto_region_name
role = os.environ.get("SAGEMAKER_ROLE_ARN") or get_execution_role()

# Params (can be overridden by CI)
project = ParameterString(name="ProjectName", default_value="retail-forecast")
data_bucket = ParameterString(name="S3DataBucket", default_value="REPLACE_ME-data")
artifacts_bucket = ParameterString(name="S3ArtifactsBucket", default_value="REPLACE_ME-artifacts")
training_image = ParameterString(name="TrainingImageUri", default_value="683313688378.dkr.ecr.ap-southeast-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3")
instance_type = ParameterString(name="InstanceType", default_value="ml.m5.xlarge")
instance_count = ParameterInteger(name="InstanceCount", default_value=1)
model_pkg_group = ParameterString(name="ModelPackageGroupName", default_value="retail-forecast")
approval_status = ParameterString(name="ModelApprovalStatus", default_value="PendingManualApproval")

cache = CacheConfig(enable_caching=True, expire_after="30d")

# --- Training step ---
estimator = SKLearn(
    entry_point=os.environ.get("TRAIN_ENTRYPOINT","train.py"),
    role=role,
    framework_version="1.2-1",
    instance_type=instance_type,
    instance_count=instance_count,
    sagemaker_session=session,
    image_uri=training_image,
    output_path=f"s3://{artifacts_bucket}/models",
    base_job_name=f"{project.default_value}-train"
)

train_step = TrainingStep(
    name="TrainModel",
    estimator=estimator,
    inputs={'train': sagemaker.inputs.TrainingInput(f"s3://{data_bucket}/train/")},
    cache_config=cache
)

# --- Evaluation step ---
processor = ScriptProcessor(
    image_uri=training_image,
    role=role,
    command=["python3"],
    instance_type=instance_type,
    instance_count=1,
    sagemaker_session=session,
    base_job_name=f"{project.default_value}-eval"
)

eval_step = ProcessingStep(
    name="EvaluateModel",
    processor=processor,
    inputs=[
        ProcessingInput(source=train_step.properties.ModelArtifacts.S3ModelArtifacts, destination="/opt/ml/processing/model"),
        ProcessingInput(source=f"s3://{data_bucket}/test/", destination="/opt/ml/processing/test")
    ],
    outputs=[
        ProcessingOutput(output_name="metrics", source="/opt/ml/processing/metrics")
    ],
    code=os.environ.get("EVAL_ENTRYPOINT","processing_evaluate.py"),
    cache_config=cache
)

metric_artifact = MetricsSource(
    s3_uri=eval_step.properties.ProcessingOutputConfig.Outputs["metrics"].S3Output.S3Uri,
    content_type="application/json"
)
model_metrics = ModelMetrics(model_statistics=metric_artifact)

# --- Register model step ---
model = sagemaker.model.Model(
    image_uri=training_image,
    model_data=train_step.properties.ModelArtifacts.S3ModelArtifacts,
    role=role
)

register_step = ModelStep(
    name="RegisterModel",
    step_args=model.register(
        content_types=['application/json'],
        response_types=['application/json'],
        inference_instances=['ml.t3.medium','ml.m5.large'],
        transform_instances=['ml.m5.large'],
        model_package_group_name=model_pkg_group,
        model_metrics=model_metrics,
        approval_status=approval_status
    )
)

pipeline = Pipeline(
    name=f"{project.default_value}-pipeline",
    parameters=[project, data_bucket, artifacts_bucket, training_image, instance_type, instance_count, model_pkg_group, approval_status],
    steps=[train_step, eval_step, register_step],
    sagemaker_session=session
)

def main():
  import argparse
  p = argparse.ArgumentParser()
  p.add_argument("--export", action="store_true")
  args = p.parse_args()
  if args.export:
    print(pipeline.definition())
  else:
    pipeline.upsert(role_arn=role)
    execution = pipeline.start()
    print("Pipeline execution started:", execution.arn)

if __name__ == "__main__":
  main()
