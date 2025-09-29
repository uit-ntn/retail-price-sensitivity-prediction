# Azure Kubernetes Service - Retail Forecast MLOps

Thư mục này chứa **Kubernetes manifests** để triển khai ứng dụng Retail Forecast lên **Azure Kubernetes Service (AKS)**.

---

## 📁 Cấu trúc thư mục

```
k8s/
├── deployment.yaml          # Kubernetes Deployment manifest
├── service.yaml            # Service exposure configuration
├── hpa.yaml               # Horizontal Pod Autoscaler
└── README.MD              # File này
```

---

## 🎯 Core Manifests

### `deployment.yaml` - Application Deployment
**Kubernetes Deployment** cho inference API:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retail-forecast-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: forecast
  template:
    metadata:
      labels:
        app: forecast
    spec:
      containers:
      - name: forecast-api
        image: <ACR_NAME>.azurecr.io/infer:latest
        ports:
        - containerPort: 80
        env:
        - name: MODEL_PATH
          value: /app/model
```

**Configuration:**
- **Replicas:** 3 pods cho high availability
- **Container Image:** Từ Azure Container Registry
- **Port:** 80 (HTTP traffic)
- **Environment:** Model path configuration

**Key Features:**
- **Rolling Updates:** Zero-downtime deployments
- **Pod Labels:** `app: forecast` cho service selection
- **Resource Management:** CPU/memory requests và limits
- **Health Checks:** Readiness và liveness probes

### `service.yaml` - Service Exposure
**Kubernetes Service** để expose API:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: retail-forecast-service
spec:
  selector:
    app: forecast
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
```

**Configuration:**
- **Type:** ClusterIP (internal access)
- **Port Mapping:** 80 → 80
- **Selector:** Targets pods với label `app: forecast`

**Service Types:**
- **ClusterIP:** Internal cluster access only
- **LoadBalancer:** External access với Azure Load Balancer
- **NodePort:** Access via node IP và port

### `hpa.yaml` - Horizontal Pod Autoscaler
**Auto-scaling** configuration:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: retail-forecast-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: retail-forecast-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Auto-scaling Features:**
- **Min Replicas:** 2 pods (always available)
- **Max Replicas:** 10 pods (cost control)
- **CPU Target:** 70% utilization
- **Scaling Policy:** Gradual scale up/down

---

## 🚀 Deployment Workflow

### 1. **Prerequisites**
```bash
# Connect to AKS cluster
az aks get-credentials --resource-group retail-dev-rg --name aks-mlops-prod

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### 2. **Deploy Application**
```bash
# Apply all manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

# Or apply all at once
kubectl apply -f .
```

### 3. **Verify Deployment**
```bash
# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get hpa

# Check pod logs
kubectl logs -l app=forecast

# Describe resources for troubleshooting
kubectl describe deployment retail-forecast-api
```

### 4. **Test Application**
```bash
# Port forward for local testing
kubectl port-forward service/retail-forecast-service 8080:80

# Test API endpoint
curl http://localhost:8080/health
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"data": [[1,2,3,4]]}'
```

---

## 🔧 Configuration Management

### Environment Variables:
```yaml
# In deployment.yaml
env:
- name: MODEL_PATH
  value: /app/model
- name: AZURE_CLIENT_ID
  valueFrom:
    secretKeyRef:
      name: azure-credentials
      key: client-id
- name: APPLICATIONINSIGHTS_CONNECTION_STRING
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: app-insights-connection
```

### ConfigMap Example:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app-insights-connection: "InstrumentationKey=..."
  model-endpoint: "https://retail-forecast-endpoint.azureml.net/score"
  log-level: "INFO"
```

### Secret Example:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: azure-credentials
type: Opaque
data:
  client-id: <base64-encoded-client-id>
  client-secret: <base64-encoded-client-secret>
```

---

## 📊 Monitoring & Health Checks

### Health Probes:
```yaml
# In deployment.yaml containers section
livenessProbe:
  httpGet:
    path: /health
    port: 80
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /ready
    port: 80
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Resource Limits:
```yaml
# In deployment.yaml containers section
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### Monitoring Commands:
```bash
# Monitor pod resource usage
kubectl top pods -l app=forecast

# Watch HPA scaling
kubectl get hpa -w

# Monitor deployment rollout
kubectl rollout status deployment/retail-forecast-api

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

---

## 🔄 Deployment Strategies

### 1. **Rolling Update (Default)**
```yaml
# In deployment.yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

**Benefits:**
- Zero downtime
- Gradual rollout
- Easy rollback

### 2. **Blue-Green Deployment**
```bash
# Deploy new version với different label
kubectl apply -f deployment-green.yaml

# Test green deployment
kubectl port-forward service/retail-forecast-service-green 8080:80

# Switch traffic
kubectl patch service retail-forecast-service -p '{"spec":{"selector":{"version":"green"}}}'

# Cleanup old version
kubectl delete deployment retail-forecast-api-blue
```

### 3. **Canary Deployment**
```yaml
# deployment-canary.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retail-forecast-api-canary
spec:
  replicas: 1  # Small percentage of traffic
  selector:
    matchLabels:
      app: forecast
      version: canary
```

---

## 🔐 Security Best Practices

### Pod Security:
```yaml
# In deployment.yaml template spec
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000
containers:
- name: forecast-api
  securityContext:
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
    capabilities:
      drop:
      - ALL
```

### Network Policies:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: retail-forecast-netpol
spec:
  podSelector:
    matchLabels:
      app: forecast
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
```

### Service Account:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: retail-forecast-sa
  annotations:
    azure.workload.identity/client-id: "your-client-id"
---
# In deployment.yaml template spec
serviceAccountName: retail-forecast-sa
```

---

## 🌐 Ingress Configuration

### NGINX Ingress:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: retail-forecast-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  tls:
  - hosts:
    - api.retail-forecast.com
    secretName: retail-forecast-tls
  rules:
  - host: api.retail-forecast.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: retail-forecast-service
            port:
              number: 80
```

### Application Gateway Ingress:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: retail-forecast-agic
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
    appgw.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
  - host: api.retail-forecast.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: retail-forecast-service
            port:
              number: 80
```

---

## 📈 Scaling Strategies

### Horizontal Pod Autoscaler (HPA):
```bash
# Create HPA với kubectl
kubectl autoscale deployment retail-forecast-api \
  --cpu-percent=70 \
  --min=2 \
  --max=10

# Custom metrics HPA
kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: retail-forecast-hpa-custom
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: retail-forecast-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
EOF
```

### Vertical Pod Autoscaler (VPA):
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: retail-forecast-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: retail-forecast-api
  updatePolicy:
    updateMode: "Auto"
```

### Cluster Autoscaler:
```bash
# AKS cluster autoscaler
az aks update \
  --resource-group retail-dev-rg \
  --name aks-mlops-prod \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 5
```

---

## 🔧 Advanced Configurations

### Init Containers:
```yaml
# In deployment.yaml template spec
initContainers:
- name: model-downloader
  image: azure/cli:latest
  command:
  - sh
  - -c
  - |
    az ml model download \
      --name retail-forecast \
      --version latest \
      --download-path /shared/model
  volumeMounts:
  - name: model-volume
    mountPath: /shared
volumes:
- name: model-volume
  emptyDir: {}
```

### Sidecar Containers:
```yaml
# In deployment.yaml containers section
- name: log-shipper
  image: fluent/fluent-bit:latest
  volumeMounts:
  - name: app-logs
    mountPath: /var/log/app
  - name: fluent-bit-config
    mountPath: /fluent-bit/etc
```

### Pod Disruption Budget:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: retail-forecast-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: forecast
```

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. **Pod Not Starting**
```bash
# Check pod status
kubectl get pods -l app=forecast

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check resource constraints
kubectl top pods
kubectl describe nodes
```

#### 2. **Service Not Accessible**
```bash
# Check service endpoints
kubectl get endpoints retail-forecast-service

# Test service connectivity
kubectl run test-pod --image=nginx --rm -i --tty -- bash
# Inside pod: curl http://retail-forecast-service/health

# Check network policies
kubectl get networkpolicies
```

#### 3. **HPA Not Scaling**
```bash
# Check HPA status
kubectl describe hpa retail-forecast-hpa

# Check metrics server
kubectl get pods -n kube-system | grep metrics-server

# Test CPU load
kubectl run load-generator --image=busybox --rm -i --tty -- sh
# Inside: while true; do wget -q -O- http://retail-forecast-service/predict; done
```

#### 4. **Image Pull Issues**
```bash
# Check ACR integration
az aks check-acr --resource-group retail-dev-rg --name aks-mlops-prod --acr acrretaildev

# Check image exists
az acr repository list --name acrretaildev
az acr repository show-tags --name acrretaildev --repository retail/infer

# Check pod events
kubectl describe pod <pod-name> | grep Events -A 10
```

---

## 💰 Cost Optimization

### Resource Optimization:
```yaml
# Right-size resource requests
resources:
  requests:
    cpu: 50m      # 0.05 CPU cores
    memory: 128Mi # 128 MiB RAM
  limits:
    cpu: 200m     # 0.2 CPU cores
    memory: 256Mi # 256 MiB RAM
```

### Scaling Optimization:
```yaml
# Aggressive scale-down
spec:
  minReplicas: 1  # Scale to 1 during low traffic
  maxReplicas: 5  # Lower max replicas
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### Node Optimization:
```bash
# Use spot instances
az aks nodepool add \
  --resource-group retail-dev-rg \
  --cluster-name aks-mlops-prod \
  --name spot \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 3
```

---

## 📚 Tài liệu tham khảo

- [Azure Kubernetes Service Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Azure Container Registry with AKS](https://docs.microsoft.com/en-us/azure/aks/cluster-container-registry-integration)
- [AKS Best Practices](https://docs.microsoft.com/en-us/azure/aks/best-practices)
