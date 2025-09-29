# Azure Monitoring - Retail Forecast MLOps

Thư mục này chứa **monitoring, alerting, và observability** configurations cho Retail Forecast MLOps pipeline trên **Microsoft Azure**.

---

## 📁 Cấu trúc thư mục

```
monitor/
├── alerts.bicep             # Application Insights alerts configuration
├── kql/                    # KQL queries cho monitoring
│   ├── error.kql          # Error tracking queries
│   └── latency.kql        # Latency monitoring queries
└── README.MD              # File này
```

---

## 📊 Application Insights Alerts (`alerts.bicep`)

### Alert Configuration
**Bicep template** cho Application Insights monitoring alerts:

```bicep
param location string
@description('Resource ID of the Application Insights component')
param appInsightsId string
@description('Optional Action Group resource ID for notifications')
param actionGroupId string = ''

var alertGroup = empty(actionGroupId) ? [] : [
  {
    actionGroupId: actionGroupId
  }
]
```

### 1. **P95 Latency Alert**
**High Response Time** monitoring:

```bicep
resource p95Latency 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'ai-p95-latency-high'
  location: location
  properties: {
    severity: 2
    enabled: true
    scopes: [appInsightsId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    autoMitigate: true
    criteria: {
      allOf: [
        {
          name: 'p95Duration'
          metricName: 'requests/duration'
          metricNamespace: 'microsoft.insights/components'
          operator: 'GreaterThan'
          threshold: 400
          timeAggregation: 'Percentile95'
          dimensions: []
        }
      ]
    }
    actions: alertGroup
  }
}
```

**Configuration:**
- **Trigger:** P95 response time > 400ms
- **Evaluation:** Every 1 minute, 5-minute window
- **Severity:** Warning (2)
- **Auto-mitigation:** Enabled

**Use Cases:**
- API performance degradation
- High traffic load detection
- Infrastructure bottlenecks
- Model inference slowdown

### 2. **Error Rate Alert**
**5XX Error Rate** monitoring:

```bicep
resource errorRate 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'ai-5xx-rate-high'
  location: location
  properties: {
    severity: 2
    enabled: true
    scopes: [appInsightsId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    autoMitigate: true
    criteria: {
      allOf: [
        {
          name: 'failedRequests'
          metricName: 'requests/failed'
          metricNamespace: 'microsoft.insights/components'
          operator: 'GreaterThan'
          threshold: 1
          timeAggregation: 'Total'
          dimensions: []
        }
      ]
    }
    actions: alertGroup
  }
}
```

**Configuration:**
- **Trigger:** Any failed requests (> 1 per 5 minutes)
- **Evaluation:** Every 1 minute, 5-minute window
- **Severity:** Warning (2)
- **Auto-mitigation:** Enabled

**Use Cases:**
- API server crashes
- Model loading failures
- Authentication issues
- Resource exhaustion

---

## 🔍 KQL Queries (`kql/`)

### `error.kql` - Error Monitoring
**KQL query** để track errors và failed requests:

```kql
requests
| where success == false or toint(resultCode) >= 500
| summarize failures=count() by bin(timestamp, 5m), resultCode, tostring(operation_Name)
| order by timestamp desc
```

**Query Features:**
- **Filter Criteria:** Failed requests hoặc 5xx status codes
- **Time Binning:** 5-minute aggregation
- **Grouping:** By result code và operation name
- **Sorting:** Most recent errors first

**Usage:**
```bash
# Run query trong Azure Portal
1. Navigate to Application Insights → Logs
2. Copy paste query từ error.kql
3. Adjust time range as needed
4. Export results hoặc create alert
```

**Analysis Examples:**
```kql
// Top error operations
requests
| where success == false
| summarize ErrorCount=count() by operation_Name
| order by ErrorCount desc
| take 10

// Error trend over time
requests
| where success == false
| summarize ErrorCount=count() by bin(timestamp, 1h)
| render timechart

// Error details với stack traces
requests
| where success == false
| join kind=inner exceptions on operation_Id
| project timestamp, operation_Name, resultCode, exception_type, exception_message
| order by timestamp desc
```

### `latency.kql` - Latency Monitoring
**KQL query** để track response time metrics:

```kql
requests
| summarize
    p50=percentile(duration, 50),
    p95=percentile(duration, 95),
    p99=percentile(duration, 99)
  by bin(timestamp, 5m), tostring(cloud_RoleName)
| order by timestamp desc
```

**Query Features:**
- **Percentile Metrics:** P50, P95, P99 response times
- **Time Binning:** 5-minute aggregation
- **Grouping:** By cloud role name (service)
- **Sorting:** Most recent data first

**Performance Analysis:**
```kql
// Slowest endpoints
requests
| summarize AvgDuration=avg(duration), P95Duration=percentile(duration, 95) by url
| where P95Duration > 1000  // > 1 second
| order by P95Duration desc

// Performance by operation
requests
| summarize 
    RequestCount=count(),
    AvgDuration=avg(duration),
    P95Duration=percentile(duration, 95)
  by operation_Name
| order by P95Duration desc

// Performance trend analysis
requests
| where timestamp > ago(24h)
| summarize P95Duration=percentile(duration, 95) by bin(timestamp, 1h)
| render timechart
```

---

## 🚀 Deployment Workflow

### 1. **Prerequisites**
```bash
# Ensure Application Insights exists
az monitor app-insights component show \
  --app retail-dev-appi \
  --resource-group retail-dev-rg

# Get Application Insights resource ID
APP_INSIGHTS_ID=$(az monitor app-insights component show \
  --app retail-dev-appi \
  --resource-group retail-dev-rg \
  --query id -o tsv)
```

### 2. **Deploy Alerts**
```bash
# Deploy alerts với Bicep
az deployment group create \
  --resource-group retail-dev-rg \
  --template-file alerts.bicep \
  --parameters \
    location=southeastasia \
    appInsightsId="$APP_INSIGHTS_ID"

# With action group for notifications
az deployment group create \
  --resource-group retail-dev-rg \
  --template-file alerts.bicep \
  --parameters \
    location=southeastasia \
    appInsightsId="$APP_INSIGHTS_ID" \
    actionGroupId="/subscriptions/.../actionGroups/retail-alerts"
```

### 3. **Verify Alerts**
```bash
# List deployed alerts
az monitor metrics alert list \
  --resource-group retail-dev-rg

# Check alert status
az monitor metrics alert show \
  --name ai-p95-latency-high \
  --resource-group retail-dev-rg
```

---

## 📈 Advanced Monitoring Setup

### Action Group Configuration:
```bash
# Create action group cho notifications
az monitor action-group create \
  --name retail-alerts \
  --resource-group retail-dev-rg \
  --action email admin admin@company.com \
  --action sms mobile +1234567890 \
  --action webhook webhook https://hooks.slack.com/services/...
```

### Custom Metrics:
```python
# Python application code
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import metrics
import logging

# Configure Application Insights
configure_azure_monitor(
    connection_string="InstrumentationKey=..."
)

# Custom metrics
meter = metrics.get_meter(__name__)
prediction_counter = meter.create_counter(
    name="ml_predictions_total",
    description="Total number of ML predictions"
)
prediction_latency = meter.create_histogram(
    name="ml_prediction_duration_ms",
    description="ML prediction latency in milliseconds"
)

# Usage in API
@app.post("/predict")
async def predict(data: PredictionRequest):
    start_time = time.time()
    
    # Make prediction
    result = model.predict(data.features)
    
    # Record metrics
    prediction_counter.add(1)
    prediction_latency.record((time.time() - start_time) * 1000)
    
    return {"prediction": result}
```

### Log Analytics Queries:
```kql
// Custom events tracking
customEvents
| where name == "ModelPrediction"
| summarize PredictionCount=count() by bin(timestamp, 5m)
| render timechart

// Dependency tracking
dependencies
| where type == "Azure ML"
| summarize 
    CallCount=count(),
    AvgDuration=avg(duration),
    SuccessRate=countif(success == true) * 100.0 / count()
  by bin(timestamp, 5m)
| render timechart
```

---

## 🔔 Alert Management

### Alert Rules:
```bash
# Create custom metric alert
az monitor metrics alert create \
  --name "ml-model-accuracy-low" \
  --resource-group retail-dev-rg \
  --scopes "$APP_INSIGHTS_ID" \
  --condition "avg customMetrics/ModelAccuracy < 0.8" \
  --description "Model accuracy below threshold" \
  --evaluation-frequency 5m \
  --window-size 15m \
  --severity 2

# Create availability test alert
az monitor metrics alert create \
  --name "api-availability-low" \
  --resource-group retail-dev-rg \
  --scopes "$APP_INSIGHTS_ID" \
  --condition "avg availabilityResults/availabilityPercentage < 95" \
  --description "API availability below 95%" \
  --evaluation-frequency 1m \
  --window-size 5m \
  --severity 1
```

### Alert Actions:
```bash
# Update alert với action group
az monitor metrics alert update \
  --name ai-p95-latency-high \
  --resource-group retail-dev-rg \
  --add-action "/subscriptions/.../actionGroups/retail-alerts"

# Disable alert temporarily
az monitor metrics alert update \
  --name ai-p95-latency-high \
  --resource-group retail-dev-rg \
  --enabled false
```

---

## 📊 Dashboard & Visualization

### Azure Dashboard:
```json
{
  "lenses": {
    "0": {
      "order": 0,
      "parts": {
        "0": {
          "position": {"x": 0, "y": 0, "rowSpan": 4, "colSpan": 6},
          "metadata": {
            "inputs": [
              {
                "name": "resourceTypeMode",
                "isOptional": true
              },
              {
                "name": "ComponentId",
                "value": {
                  "SubscriptionId": "...",
                  "ResourceGroup": "retail-dev-rg",
                  "Name": "retail-dev-appi"
                }
              }
            ],
            "type": "Extension/HubsExtension/PartType/MonitorChartPart"
          }
        }
      }
    }
  }
}
```

### Workbook Templates:
```kql
// Performance overview
let timeRange = range(now(-1d), now(), 5m);
requests
| summarize 
    RequestCount=count(),
    SuccessRate=countif(success == true) * 100.0 / count(),
    P95Latency=percentile(duration, 95)
  by bin(timestamp, 5m)
| join kind=fullouter timeRange on timestamp
| project 
    timestamp=coalesce(timestamp, timestamp1),
    RequestCount=coalesce(RequestCount, 0),
    SuccessRate=coalesce(SuccessRate, 100),
    P95Latency=coalesce(P95Latency, 0)
| render timechart
```

---

## 🔧 Configuration Management

### Environment Variables:
```bash
# Required for monitoring setup
export RESOURCE_GROUP="retail-dev-rg"
export APP_INSIGHTS_NAME="retail-dev-appi"
export ACTION_GROUP_NAME="retail-alerts"

# Optional configurations
export ALERT_EMAIL="admin@company.com"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

### Bicep Parameters:
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": {
      "value": "southeastasia"
    },
    "appInsightsId": {
      "value": "/subscriptions/.../resourceGroups/retail-dev-rg/providers/Microsoft.Insights/components/retail-dev-appi"
    },
    "actionGroupId": {
      "value": "/subscriptions/.../resourceGroups/retail-dev-rg/providers/microsoft.insights/actionGroups/retail-alerts"
    }
  }
}
```

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. **Alerts Not Triggering**
```bash
# Check alert rule configuration
az monitor metrics alert show \
  --name ai-p95-latency-high \
  --resource-group retail-dev-rg

# Check metric data availability
az monitor metrics list-definitions \
  --resource "$APP_INSIGHTS_ID"

# Test alert condition manually
az monitor metrics list \
  --resource "$APP_INSIGHTS_ID" \
  --metric "requests/duration" \
  --aggregation Percentile95
```

#### 2. **Missing Application Insights Data**
```bash
# Check instrumentation key
az monitor app-insights component show \
  --app retail-dev-appi \
  --resource-group retail-dev-rg \
  --query instrumentationKey

# Verify connection string
az monitor app-insights component show \
  --app retail-dev-appi \
  --resource-group retail-dev-rg \
  --query connectionString
```

#### 3. **KQL Query Errors**
```kql
// Check data availability
requests
| where timestamp > ago(1h)
| take 10

// Verify schema
requests
| getschema

// Check for missing columns
requests
| where timestamp > ago(1h)
| project timestamp, duration, success, resultCode
| take 5
```

#### 4. **Action Group Not Working**
```bash
# Test action group
az monitor action-group test-notifications create \
  --action-group-id "/subscriptions/.../actionGroups/retail-alerts" \
  --alert-type "servicehealth" \
  --notification-type "email"

# Check action group history
az monitor activity-log list \
  --resource-group retail-dev-rg \
  --caller "Microsoft.Insights/ActionGroups"
```

---

## 💰 Cost Optimization

### Data Retention:
```bash
# Set Application Insights retention
az monitor app-insights component update \
  --app retail-dev-appi \
  --resource-group retail-dev-rg \
  --retention-time 90  # 90 days

# Configure sampling
az monitor app-insights component update \
  --app retail-dev-appi \
  --resource-group retail-dev-rg \
  --sampling-percentage 50  # 50% sampling
```

### Query Optimization:
```kql
// Use time filters to reduce data scan
requests
| where timestamp > ago(1h)  // Instead of scanning all data
| summarize count() by bin(timestamp, 5m)

// Use specific columns only
requests
| where timestamp > ago(1h)
| project timestamp, duration, success  // Instead of all columns
| summarize avg(duration) by bin(timestamp, 5m)
```

---

## 📚 Tài liệu tham khảo

- [Azure Application Insights Documentation](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [KQL (Kusto Query Language) Reference](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Azure Monitor Alerts](https://docs.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview)
- [Application Insights Telemetry](https://docs.microsoft.com/en-us/azure/azure-monitor/app/data-model)
- [Azure Monitor Bicep Templates](https://docs.microsoft.com/en-us/azure/azure-monitor/resource-manager-samples)
