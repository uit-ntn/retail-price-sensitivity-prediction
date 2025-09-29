# AWS Observability - Retail Forecast MLOps

Thư mục này chứa tất cả cấu hình **monitoring, logging, và alerting** cho Retail Forecast MLOps pipeline trên **Amazon Web Services**.

---

## 📁 Cấu trúc thư mục

```
observability/
├── cloudwatch-alarms/          # CloudWatch Alarms
│   └── alarms.tf              # Terraform alarms configuration
│
├── cloudwatch-logs/           # Logging infrastructure
│   └── fluent-bit-daemonset.yaml  # Fluent Bit log collection
│
└── README.MD                  # File này
```

---

## 📊 CloudWatch Alarms (`cloudwatch-alarms/`)

### `alarms.tf`
**Terraform configuration** cho CloudWatch alarms:

#### Variables:
```hcl
variable "alb_arn_suffix" {
  type        = string
  description = "ALB ARN suffix (e.g., app/abc123/def456)"
}

variable "cluster_name" {
  type        = string
  description = "EKS cluster name for alarm naming"
}
```

#### Alarms được tạo:

### 1. **ALB 5XX Error Alarm**
**Chức năng:**
- Monitor Application Load Balancer 5xx errors
- Trigger khi có ≥5 5xx errors trong 1 phút
- Detect backend service issues

**Configuration:**
- **Metric:** `HTTPCode_ELB_5XX_Count`
- **Namespace:** `AWS/ApplicationELB`
- **Threshold:** 5 errors
- **Period:** 60 seconds
- **Evaluation:** 1 period

**Use Cases:**
- API server crashes
- Backend service unavailable
- Configuration errors
- Resource exhaustion

### 2. **EKS High CPU Alarm**
**Chức năng:**
- Monitor EKS node CPU utilization
- Trigger khi CPU > 80% trong 2 periods liên tiếp
- Detect resource constraints

**Configuration:**
- **Metric:** `node_cpu_utilization`
- **Namespace:** `CWAgent`
- **Threshold:** 80%
- **Period:** 60 seconds
- **Evaluation:** 2 periods

**Use Cases:**
- High traffic loads
- Resource-intensive workloads
- Need for horizontal scaling
- Performance optimization

---

## 📝 CloudWatch Logs (`cloudwatch-logs/`)

### `fluent-bit-daemonset.yaml`
**Fluent Bit DaemonSet** cho log collection:

#### Components:

### 1. **Namespace**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: amazon-cloudwatch
```

**Chức năng:**
- Tách biệt monitoring resources
- Organized log collection components

### 2. **ConfigMap**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-cluster-info
  namespace: amazon-cloudwatch
data:
  cluster.name: REPLACE_ME_EKS_CLUSTER_NAME
  logs.region: REPLACE_ME_AWS_REGION
  http.server: "On"
  http.port: "2020"
```

**Configuration:**
- **cluster.name:** EKS cluster identifier
- **logs.region:** AWS region cho CloudWatch Logs
- **http.server:** Enable HTTP monitoring endpoint
- **http.port:** Monitoring port (2020)

### 3. **DaemonSet**
**Fluent Bit pods** chạy trên mỗi node:

**Features:**
- **Image:** `public.ecr.aws/aws-observability/aws-for-fluent-bit:stable`
- **Resource Limits:** 200Mi memory
- **Resource Requests:** 100m CPU, 100Mi memory
- **Volume Mounts:** Host log directories

**Log Sources:**
- `/var/log` - System logs
- `/var/lib/docker/containers` - Container logs

### 4. **ServiceAccount**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fluent-bit
  namespace: amazon-cloudwatch
  annotations:
    eks.amazonaws.com/role-arn: REPLACE_ME_IRSA_FOR_CLOUDWATCH
```

**IRSA Integration:**
- IAM Role for Service Account
- CloudWatch Logs write permissions
- Secure credential management

---

## 🚀 Deployment Workflow

### 1. Deploy CloudWatch Alarms

#### Prerequisites:
```bash
# Get ALB ARN suffix
ALB_ARN=$(aws elbv2 describe-load-balancers --query 'LoadBalancers[?contains(LoadBalancerName, `retail`)].LoadBalancerArn' --output text)
ALB_SUFFIX=$(echo $ALB_ARN | cut -d'/' -f2-)

# Set variables
export TF_VAR_alb_arn_suffix="$ALB_SUFFIX"
export TF_VAR_cluster_name="retail-mlops-dev"
```

#### Deploy Alarms:
```bash
cd cloudwatch-alarms

# Initialize Terraform
terraform init

# Plan deployment
terraform plan \
  -var="alb_arn_suffix=$ALB_SUFFIX" \
  -var="cluster_name=retail-mlops-dev"

# Apply configuration
terraform apply \
  -var="alb_arn_suffix=$ALB_SUFFIX" \
  -var="cluster_name=retail-mlops-dev"
```

#### Verify Alarms:
```bash
# List CloudWatch alarms
aws cloudwatch describe-alarms --alarm-names "retail-mlops-dev-alb-5xx" "retail-mlops-dev-cpu-high"

# Check alarm state
aws cloudwatch describe-alarms --state-value ALARM
```

### 2. Deploy Fluent Bit Logging

#### Prerequisites:
```bash
# Set cluster and region
export CLUSTER_NAME="retail-mlops-dev"
export AWS_REGION="ap-southeast-1"

# Create IRSA for Fluent Bit (optional)
eksctl create iamserviceaccount \
  --cluster=$CLUSTER_NAME \
  --namespace=amazon-cloudwatch \
  --name=fluent-bit \
  --attach-policy-arn=arn:aws:iam::aws:policy/CloudWatchLogsFullAccess \
  --approve
```

#### Configure and Deploy:
```bash
cd cloudwatch-logs

# Update configuration
sed -i "s/REPLACE_ME_EKS_CLUSTER_NAME/$CLUSTER_NAME/g" fluent-bit-daemonset.yaml
sed -i "s/REPLACE_ME_AWS_REGION/$AWS_REGION/g" fluent-bit-daemonset.yaml

# Get IRSA role ARN (if created)
IRSA_ROLE_ARN=$(aws iam get-role --role-name eksctl-$CLUSTER_NAME-addon-iamserviceaccount-amazon-cloudwatch-fluent-bit-Role1 --query 'Role.Arn' --output text)
sed -i "s|REPLACE_ME_IRSA_FOR_CLOUDWATCH|$IRSA_ROLE_ARN|g" fluent-bit-daemonset.yaml

# Deploy Fluent Bit
kubectl apply -f fluent-bit-daemonset.yaml
```

#### Verify Deployment:
```bash
# Check Fluent Bit pods
kubectl get pods -n amazon-cloudwatch

# Check logs
kubectl logs -f daemonset/fluent-bit -n amazon-cloudwatch

# Verify log streams in CloudWatch
aws logs describe-log-groups --log-group-name-prefix "/aws/eks/$CLUSTER_NAME"
```

---

## 📈 Monitoring Dashboard

### CloudWatch Metrics

#### ALB Metrics:
```bash
# View ALB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name HTTPCode_ELB_5XX_Count \
  --dimensions Name=LoadBalancer,Value=$ALB_SUFFIX \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 300 \
  --statistics Sum
```

#### EKS Metrics:
```bash
# View node CPU metrics
aws cloudwatch get-metric-statistics \
  --namespace CWAgent \
  --metric-name node_cpu_utilization \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 300 \
  --statistics Average
```

### Log Analysis

#### Application Logs:
```bash
# Query application logs
aws logs filter-log-events \
  --log-group-name "/aws/eks/$CLUSTER_NAME/application" \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "ERROR"
```

#### Container Logs:
```bash
# Query container logs
aws logs filter-log-events \
  --log-group-name "/aws/eks/$CLUSTER_NAME/containers" \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "[timestamp, request_id, level=\"ERROR\"]"
```

---

## 🔔 Alerting Configuration

### SNS Topic Setup:
```bash
# Create SNS topic for alerts
aws sns create-topic --name retail-mlops-alerts

# Subscribe email to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-southeast-1:ACCOUNT_ID:retail-mlops-alerts \
  --protocol email \
  --notification-endpoint your-email@company.com
```

### Update Alarms with SNS:
```hcl
# Add to alarms.tf
resource "aws_sns_topic" "alerts" {
  name = "retail-mlops-alerts"
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  # ... existing configuration ...
  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
}
```

---

## 🔍 Log Queries & Analysis

### Common CloudWatch Insights Queries:

#### 1. **Error Rate Analysis**
```sql
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
| sort @timestamp desc
```

#### 2. **Response Time Analysis**
```sql
fields @timestamp, @message
| filter @message like /response_time/
| parse @message "response_time: * ms" as response_time
| stats avg(response_time), max(response_time), min(response_time) by bin(5m)
| sort @timestamp desc
```

#### 3. **Request Volume Analysis**
```sql
fields @timestamp, @message
| filter @message like /GET|POST|PUT|DELETE/
| parse @message "* * *" as method, path, status
| stats count() by method, bin(5m)
| sort @timestamp desc
```

#### 4. **Container Restart Analysis**
```sql
fields @timestamp, @message
| filter @message like /Started container/ or @message like /Stopped container/
| stats count() by bin(1h)
| sort @timestamp desc
```

---

## 📊 Custom Metrics

### Application Metrics:
```python
# Example: Custom metrics in Python application
import boto3

cloudwatch = boto3.client('cloudwatch')

def put_custom_metric(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='RetailForecast/Application',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Dimensions': [
                    {
                        'Name': 'Environment',
                        'Value': 'production'
                    }
                ]
            }
        ]
    )

# Usage examples
put_custom_metric('PredictionRequests', 1)
put_custom_metric('ModelAccuracy', 0.95, 'Percent')
put_custom_metric('ProcessingTime', 150, 'Milliseconds')
```

### Business Metrics:
```bash
# Create custom alarm for business metrics
aws cloudwatch put-metric-alarm \
  --alarm-name "low-prediction-accuracy" \
  --alarm-description "Model accuracy below threshold" \
  --metric-name ModelAccuracy \
  --namespace RetailForecast/Application \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 0.8 \
  --comparison-operator LessThanThreshold
```

---

## 🔧 Configuration Management

### Environment Variables:
```bash
# Required for deployment
export CLUSTER_NAME="retail-mlops-dev"
export AWS_REGION="ap-southeast-1"
export AWS_ACCOUNT_ID="123456789012"

# Optional configurations
export LOG_RETENTION_DAYS="7"
export ALARM_EMAIL="alerts@company.com"
```

### Terraform Variables:
```hcl
# terraform.tfvars
alb_arn_suffix = "app/retail-alb/1234567890abcdef"
cluster_name   = "retail-mlops-dev"
sns_topic_arn  = "arn:aws:sns:ap-southeast-1:123456789012:retail-mlops-alerts"
```

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. **Fluent Bit Not Collecting Logs**
```bash
# Check Fluent Bit status
kubectl get pods -n amazon-cloudwatch
kubectl logs -f daemonset/fluent-bit -n amazon-cloudwatch

# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn $IRSA_ROLE_ARN \
  --action-names logs:CreateLogGroup logs:CreateLogStream logs:PutLogEvents

# Verify ConfigMap
kubectl get configmap fluent-bit-cluster-info -n amazon-cloudwatch -o yaml
```

#### 2. **CloudWatch Alarms Not Triggering**
```bash
# Check alarm configuration
aws cloudwatch describe-alarms --alarm-names "retail-mlops-dev-alb-5xx"

# Check metric data availability
aws cloudwatch list-metrics --namespace AWS/ApplicationELB

# Test alarm manually
aws cloudwatch set-alarm-state \
  --alarm-name "retail-mlops-dev-alb-5xx" \
  --state-value ALARM \
  --state-reason "Testing alarm"
```

#### 3. **Missing Metrics**
```bash
# Check CloudWatch agent status (if using)
kubectl get pods -n amazon-cloudwatch | grep cloudwatch

# Verify metric filters
aws logs describe-metric-filters --log-group-name "/aws/eks/$CLUSTER_NAME/application"

# Check EKS control plane logging
aws eks describe-cluster --name $CLUSTER_NAME --query 'cluster.logging'
```

#### 4. **High CloudWatch Costs**
```bash
# Check log group retention
aws logs describe-log-groups --query 'logGroups[*].[logGroupName,retentionInDays]'

# Set log retention
aws logs put-retention-policy \
  --log-group-name "/aws/eks/$CLUSTER_NAME/application" \
  --retention-in-days 7

# Monitor usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/Logs \
  --metric-name IncomingBytes \
  --start-time $(date -d '24 hours ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 3600 \
  --statistics Sum
```

---

## 💰 Cost Optimization

### Log Management:
```bash
# Set appropriate retention periods
aws logs put-retention-policy --log-group-name "/aws/eks/$CLUSTER_NAME/application" --retention-in-days 7
aws logs put-retention-policy --log-group-name "/aws/eks/$CLUSTER_NAME/containers" --retention-in-days 3

# Delete old log groups
aws logs delete-log-group --log-group-name "/aws/eks/old-cluster/application"
```

### Metric Optimization:
```bash
# List custom metrics
aws cloudwatch list-metrics --namespace "RetailForecast/Application"

# Delete unused metrics (they expire automatically after 15 months of no data)
```

---

## 📚 Tài liệu tham khảo

- [Amazon CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [AWS for Fluent Bit](https://github.com/aws/aws-for-fluent-bit)
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)
- [EKS Control Plane Logging](https://docs.aws.amazon.com/eks/latest/userguide/control-plane-logs.html)
- [CloudWatch Container Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html)
