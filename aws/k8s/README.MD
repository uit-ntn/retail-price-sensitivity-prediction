# EKS Deployment - Retail Price Sensitivity API

## 📁 Files

- `namespace.yaml` - Create mlops namespace
- `serviceaccount.yaml` - IRSA service account for SageMaker access
- `deployment.yaml` - Main API deployment with SageMaker Registry
- `service.yaml` - LoadBalancer service
- `hpa.yaml` - Horizontal Pod Autoscaler (CPU-based)

## 🚀 Quick Deploy

**Linux/Mac:**
```bash
chmod +x apply.sh
./apply.sh
```

**Windows:**
```powershell
.\deploy.ps1
```

**Manual:**
```bash
kubectl apply -f namespace.yaml
kubectl apply -f serviceaccount.yaml
kubectl apply -f deployment.yaml 
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
```

## 🔍 Verify Deployment

```bash
# Check pods
kubectl get pods -n mlops

# Check service  
kubectl get svc -n mlops

# Get LoadBalancer URL
kubectl get svc retail-api-service -n mlops -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Test API
curl http://[LOAD_BALANCER_URL]/health
```

## 📊 Monitor

```bash
# Watch pods
kubectl get pods -n mlops -w

# Check HPA status
kubectl get hpa -n mlops

# View logs
kubectl logs -l app=retail-api -n mlops --tail=50
```