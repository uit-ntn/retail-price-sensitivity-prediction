import boto3, os
sm = boto3.client("sagemaker")

resp = sm.create_monitoring_schedule(
  MonitoringScheduleName=os.environ.get("SCHEDULE_NAME","retail-forecast-model-quality"),
  MonitoringScheduleConfig={
    "ScheduleConfig": {"ScheduleExpression": "cron(0 * * * ? *)"},
    "MonitoringJobDefinition": {
      "MonitoringAppSpecification": {
        "ImageUri": "156387875391.dkr.ecr.ap-southeast-1.amazonaws.com/sagemaker-model-monitor-analyzer"
      },
      "MonitoringInputs": [{
        "EndpointInput": {
          "EndpointName": os.environ["ENDPOINT_NAME"],
          "LocalPath": "/opt/ml/processing/input"
        }
      }],
      "MonitoringOutputConfig": {
        "MonitoringOutputs": [{
          "S3Output": {
            "LocalPath": "/opt/ml/processing/output",
            "S3Uri": f"s3://{os.environ['S3_ARTIFACTS_BUCKET']}/monitoring/model-quality",
            "S3UploadMode": "EndOfJob"
          }
        }]
      },
      "MonitoringResources": { "ClusterConfig": {"InstanceCount":1,"InstanceType":"ml.m5.large","VolumeSizeInGB":20} },
      "RoleArn": os.environ["SAGEMAKER_ROLE_ARN"]
    }
  }
)
print("Created schedule:", resp["MonitoringScheduleArn"])
