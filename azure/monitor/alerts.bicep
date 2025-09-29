param location string
@description('Resource ID of the Application Insights component')
param appInsightsId string
@description('Optional Action Group resource ID for notifications')
@allowed([
  ''
])
param actionGroupId string = ''

var alertGroup = empty(actionGroupId) ? [] : [
  {
    actionGroupId: actionGroupId
  }
]

resource p95Latency 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'ai-p95-latency-high'
  location: location
  properties: {
    severity: 2
    enabled: true
    scopes: [
      appInsightsId
    ]
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

resource errorRate 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'ai-5xx-rate-high'
  location: location
  properties: {
    severity: 2
    enabled: true
    scopes: [
      appInsightsId
    ]
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
