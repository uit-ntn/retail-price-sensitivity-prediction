import boto3, os

sm = boto3.client("sagemaker")
region = os.environ.get("AWS_REGION", "ap-southeast-1")
bucket = os.environ["S3_DATA_BUCKET"]
baseline_job_name = os.environ.get("BASELINE_JOB","retail-forecast-data-quality")

response = sm.create_data_quality_job_definition(
    JobDefinitionName=baseline_job_name,
    DataQualityBaselineConfig={"BaseliningJobName": baseline_job_name},
    DataQualityAppSpecification={
        "ImageUri": "156387875391.dkr.ecr.ap-southeast-1.amazonaws.com/sagemaker-model-monitor-analyzer",
        "ContainerArguments": []
    },
    DataQualityJobInput={
        "EndpointInput": {
            "EndpointName": os.environ["ENDPOINT_NAME"],
            "LocalPath": "/opt/ml/processing/input_data"
        }
    },
    DataQualityJobOutputConfig={
        "MonitoringOutputs": [{
            "S3Output": {
                "S3Uri": f"s3://{bucket}/monitoring/baseline",
                "LocalPath": "/opt/ml/processing/output",
                "S3UploadMode": "EndOfJob"
            }
        }]
    },
    JobResources={"ClusterConfig": {"InstanceCount": 1, "InstanceType": "ml.m5.large", "VolumeSizeInGB": 20}},
    RoleArn=os.environ["SAGEMAKER_ROLE_ARN"]
)
print("Created baseline:", response["JobDefinitionArn"])
