import boto3, os
sm = boto3.client("sagemaker")

schedule_name = os.environ.get("SCHEDULE_NAME","retail-forecast-data-quality-schedule")

resp = sm.create_monitoring_schedule(
    MonitoringScheduleName=schedule_name,
    MonitoringScheduleConfig={
        "ScheduleConfig": {"ScheduleExpression": "cron(0 * * * ? *)"}, # hourly
        "MonitoringJobDefinitionName": os.environ["DATA_QUALITY_JOB_DEF"]
    }
)
print("Created schedule:", resp["MonitoringScheduleArn"])
