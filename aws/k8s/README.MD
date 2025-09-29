# AWS Kubernetes Manifests - Retail Forecast MLOps

Thư mục này chứa tất cả **Kubernetes manifests** và **add-ons** để triển khai ứng dụng Retail Forecast lên **Amazon EKS cluster**.

---

## 📁 Cấu trúc thư mục

```
k8s/
├── addons/                    # Kubernetes cluster add-ons
│   ├── metrics-server.yaml           # Metrics collection
│   ├── cluster-autoscaler.yaml       # Node auto-scaling
│   ├── aws-load-balancer-controller.yaml  # ALB controller
│   ├── external-dns.yaml             # DNS automation
│   └── secrets-store-csi/            # AWS Secrets Manager integration
│       └── providerclass.yaml
│
├── ingress/                   # Ingress configurations
│   └── alb-ingress.yaml      # Application Load Balancer ingress
│
├── rbac/                      # Role-Based Access Control
│   └── read-only-role.yaml   # Read-only cluster role
│
├── pdb/                       # Pod Disruption Budgets
│   └── server-pdb.yaml       # Server availability protection
│
├── namespace.yaml             # Namespace definition
├── service.yaml              # Service exposure
├── hpa.yaml                  # Horizontal Pod Autoscaler
├── pod-security-standards.yaml  # Pod security policies
├── kustomization.yaml        # Kustomize configuration
└── README.MD                 # File này
```

---

## 🎯 Core Application Manifests

### `namespace.yaml`
Định nghĩa **namespace** cho ứng dụng:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: retail
```

**Chức năng:**
- Tách biệt resources theo namespace
- Áp dụng pod security standards
- Network isolation

### `service.yaml`
**Kubernetes Service** để expose inference API:

**Cấu hình:**
- **Type:** ClusterIP (internal traffic)
- **Port:** 80 → 8000 (container port)
- **Selector:** `app: retail-server`

**Sử dụng:**
```bash
# Apply service
kubectl apply -f service.yaml

# Check service
kubectl get svc -n retail
```

### `hpa.yaml`
**Horizontal Pod Autoscaler** cho auto-scaling:

**Cấu hình:**
- **Min replicas:** 2
- **Max replicas:** 10  
- **Target CPU:** 70%
- **Scale down stabilization:** 300s

**Features:**
- CPU-based scaling
- Memory-based scaling (optional)
- Custom metrics support

**Monitoring:**
```bash
# Check HPA status
kubectl get hpa -n retail

# Describe scaling events
kubectl describe hpa retail-server-hpa -n retail
```

### `pod-security-standards.yaml`
**Pod Security Standards** cho namespace:

**Security Levels:**
- **Enforce:** `baseline` - Basic security requirements
- **Audit:** `restricted` - Log violations of restricted policy
- **Warn:** `restricted` - Warning for restricted violations

**Standards:**
- Disallow privileged containers
- Require non-root user
- Restrict volume types
- Network policy enforcement

---

## 🔌 Cluster Add-ons (`addons/`)

### `metrics-server.yaml`
**Metrics Server** cho resource monitoring:

**Chức năng:**
- Collect CPU/memory metrics từ kubelet
- Enable `kubectl top` commands
- Support cho HPA scaling decisions

**Verification:**
```bash
# Check metrics server
kubectl get deployment metrics-server -n kube-system

# Test metrics collection
kubectl top nodes
kubectl top pods -n retail
```

### `cluster-autoscaler.yaml`
**Cluster Autoscaler** cho node scaling:

**Cấu hình:**
- Auto-discovery via ASG tags
- Scale-down delay: 10 minutes
- Skip nodes with local storage
- Balance similar node groups

**Features:**
- Automatic node provisioning
- Cost optimization
- Multi-AZ scaling
- Spot instance support

**Monitoring:**
```bash
# Check autoscaler logs
kubectl logs -f deployment/cluster-autoscaler -n kube-system

# Check scaling events
kubectl get events --sort-by=.metadata.creationTimestamp
```

### `aws-load-balancer-controller.yaml`
**AWS Load Balancer Controller** cho ALB/NLB:

**Chức năng:**
- Manage Application Load Balancers
- Support cho Network Load Balancers
- Integration với AWS services
- SSL termination

**Features:**
- Target type: IP mode
- WAF integration
- Cognito authentication
- Multiple protocols support

### `external-dns.yaml`
**ExternalDNS** cho DNS automation:

**Chức năng:**
- Tự động tạo DNS records
- Integration với Route53
- Support multiple DNS providers
- TTL management

**Configuration:**
- **Domain filter:** Chỉ manage specific domains
- **Policy:** `upsert-only` (safe mode)
- **Registry:** `txt` (ownership tracking)

### `secrets-store-csi/providerclass.yaml`
**AWS Secrets Manager** integration:

**Chức năng:**
- Mount secrets as volumes
- Automatic secret rotation
- Fine-grained access control
- Audit logging

**Usage:**
```yaml
# Example secret mount
volumeMounts:
- name: secrets-store
  mountPath: "/mnt/secrets"
  readOnly: true
volumes:
- name: secrets-store
  csi:
    driver: secrets-store.csi.k8s.io
    readOnly: true
    volumeAttributes:
      secretProviderClass: "retail-secrets"
```

---

## 🌐 Ingress Configuration (`ingress/`)

### `alb-ingress.yaml`
**Application Load Balancer Ingress**:

**Annotations:**
- `kubernetes.io/ingress.class: alb`
- `alb.ingress.kubernetes.io/scheme: internet-facing`
- `alb.ingress.kubernetes.io/target-type: ip`
- `alb.ingress.kubernetes.io/listen-ports: HTTP+HTTPS`

**Features:**
- **SSL Redirect:** HTTP → HTTPS (301)
- **Target Type:** IP mode (better for Fargate)
- **Health Checks:** Configurable paths
- **ExternalDNS:** Automatic DNS record creation

**Setup:**
```bash
# Update domain trong ingress file
sed -i 's/REPLACE_ME_DOMAIN/your-domain.com/g' ingress/alb-ingress.yaml

# Apply ingress
kubectl apply -f ingress/alb-ingress.yaml

# Check ALB creation
kubectl get ingress -n retail
```

---

## 🔐 RBAC Configuration (`rbac/`)

### `read-only-role.yaml`
**ClusterRole** cho read-only access:

**Permissions:**
- Get/List/Watch pods, services, deployments
- View logs và metrics
- No create/update/delete permissions

**Use Cases:**
- Monitoring tools
- CI/CD systems (read-only)
- Developer access
- Troubleshooting

**Binding:**
```bash
# Bind role to user/service account
kubectl create clusterrolebinding readonly-binding \
  --clusterrole=readonly-cluster-role \
  --user=developer@company.com
```

---

## 🛡️ Pod Disruption Budgets (`pdb/`)

### `server-pdb.yaml`
**PodDisruptionBudget** cho high availability:

**Configuration:**
- **Min Available:** 1 pod (ensure service continuity)
- **Selector:** `app: retail-server`
- **Max Unavailable:** 50% (alternative config)

**Protection:**
- Cluster upgrades
- Node maintenance
- Voluntary disruptions
- Zone failures

**Verification:**
```bash
# Check PDB status
kubectl get pdb -n retail

# Test disruption
kubectl drain NODE_NAME --ignore-daemonsets
```

---

## 🔧 Kustomization (`kustomization.yaml`)

**Kustomize configuration** để manage manifests:

**Resources included:**
- All add-ons manifests
- Security policies
- RBAC configurations
- Ingress setup

**Usage:**
```bash
# Apply all manifests với kustomize
kubectl apply -k .

# Preview changes
kubectl diff -k .

# Delete all resources
kubectl delete -k .
```

**Benefits:**
- Consistent deployment
- Environment-specific overlays
- Resource transformation
- Configuration management

---

## 🚀 Deployment Workflow

### 1. Prerequisites
```bash
# Ensure EKS cluster is running
kubectl cluster-info

# Verify node readiness
kubectl get nodes

# Check cluster add-ons
kubectl get pods -n kube-system
```

### 2. Deploy Add-ons
```bash
# Deploy essential add-ons first
kubectl apply -f addons/metrics-server.yaml
kubectl apply -f addons/cluster-autoscaler.yaml
kubectl apply -f addons/aws-load-balancer-controller.yaml

# Wait for add-ons to be ready
kubectl wait --for=condition=available --timeout=300s deployment/metrics-server -n kube-system
```

### 3. Setup Security
```bash
# Apply security policies
kubectl apply -f pod-security-standards.yaml
kubectl apply -f rbac/read-only-role.yaml
```

### 4. Deploy Application Infrastructure
```bash
# Create namespace and basic resources
kubectl apply -f namespace.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
kubectl apply -f pdb/server-pdb.yaml
```

### 5. Configure Ingress
```bash
# Update domain in ingress file
export DOMAIN="your-domain.com"
sed -i "s/REPLACE_ME_DOMAIN/$DOMAIN/g" ingress/alb-ingress.yaml

# Apply ingress
kubectl apply -f ingress/alb-ingress.yaml
```

### 6. Deploy Application
```bash
# Apply application deployment (not in this folder)
kubectl apply -f ../path/to/deployment.yaml

# Verify deployment
kubectl get all -n retail
```

---

## 📊 Monitoring & Observability

### Health Checks
```bash
# Check cluster health
kubectl get componentstatus

# Check node status
kubectl get nodes -o wide

# Check pod status
kubectl get pods -n retail -o wide
```

### Resource Usage
```bash
# Node resource usage
kubectl top nodes

# Pod resource usage
kubectl top pods -n retail

# HPA status
kubectl get hpa -n retail
```

### Logs & Events
```bash
# Application logs
kubectl logs -f deployment/retail-server -n retail

# Cluster events
kubectl get events --sort-by=.metadata.creationTimestamp

# Add-on logs
kubectl logs -f deployment/cluster-autoscaler -n kube-system
```

### Load Balancer Status
```bash
# Check ALB creation
kubectl get ingress -n retail

# Get ALB DNS name
kubectl get ingress retail-server -n retail -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Test connectivity
curl -H "Host: api.your-domain.com" http://ALB_DNS_NAME/health
```

---

## 🔧 Configuration Management

### Environment Variables
```bash
# Required for add-ons
export AWS_REGION="ap-southeast-1"
export CLUSTER_NAME="retail-mlops-dev"
export AWS_ACCOUNT_ID="123456789012"

# Optional configurations
export DOMAIN="your-domain.com"
export CERTIFICATE_ARN="arn:aws:acm:..."
```

### Customization
```bash
# Update cluster autoscaler for your ASG
sed -i "s/CLUSTER_NAME/$CLUSTER_NAME/g" addons/cluster-autoscaler.yaml

# Update external-dns domain filter
sed -i "s/DOMAIN_FILTER/$DOMAIN/g" addons/external-dns.yaml
```

---

## 🐛 Troubleshooting

### Common Issues:

1. **Metrics Server Not Working**
   ```bash
   # Check metrics server logs
   kubectl logs -f deployment/metrics-server -n kube-system
   
   # Common fix: Update kubelet certificates
   kubectl get csr | grep Pending | awk '{print $1}' | xargs kubectl certificate approve
   ```

2. **Cluster Autoscaler Not Scaling**
   ```bash
   # Check autoscaler logs
   kubectl logs -f deployment/cluster-autoscaler -n kube-system | grep -E "(scale|node)"
   
   # Verify ASG tags
   aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[?Tags[?Key==`kubernetes.io/cluster/CLUSTER_NAME`]]'
   ```

3. **ALB Not Creating**
   ```bash
   # Check load balancer controller
   kubectl logs -f deployment/aws-load-balancer-controller -n kube-system
   
   # Verify IAM permissions
   aws sts get-caller-identity
   ```

4. **ExternalDNS Not Creating Records**
   ```bash
   # Check external-dns logs
   kubectl logs -f deployment/external-dns -n kube-system
   
   # Verify Route53 permissions
   aws route53 list-hosted-zones
   ```

5. **Pod Security Standards Blocking Pods**
   ```bash
   # Check pod events
   kubectl describe pod POD_NAME -n retail
   
   # Review security context
   kubectl get pod POD_NAME -n retail -o yaml | grep -A 10 securityContext
   ```

---

## 📚 Tài liệu tham khảo

- [Amazon EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)
- [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)
- [ExternalDNS](https://github.com/kubernetes-sigs/external-dns)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
