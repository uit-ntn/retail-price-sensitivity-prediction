import boto3, os

client = boto3.client("application-autoscaling")
endpoint_name = os.getenv("ENDPOINT_NAME", "retail-mlops-endpoint")
resource_id = f"endpoint/{endpoint_name}/variant/AllTraffic"

client.register_scalable_target(
    ServiceNamespace="sagemaker",
    ResourceId=resource_id,
    ScalableDimension="sagemaker:variant:DesiredInstanceCount",
    MinCapacity=1,
    MaxCapacity=3
)

client.put_scaling_policy(
    PolicyName="cpu-scaling-policy",
    ServiceNamespace="sagemaker",
    ResourceId=resource_id,
    ScalableDimension="sagemaker:variant:DesiredInstanceCount",
    PolicyType="TargetTrackingScaling",
    TargetTrackingScalingPolicyConfiguration={
        "TargetValue": 60.0,
        "PredefinedMetricSpecification": {"PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"},
        "ScaleOutCooldown": 60,
        "ScaleInCooldown": 120
    }
)

print("Auto-scaling policy applied.")
