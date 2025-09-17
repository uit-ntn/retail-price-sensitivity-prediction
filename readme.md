# Retail Forecast MLOps (Azure + AWS)

Dự án demo **MLOps pipeline đa cloud (Azure & AWS)** cho bài toán **dự báo nhu cầu bán lẻ**.  
Ngôn ngữ: **Python**, hạ tầng bằng **Terraform / Bicep**, triển khai inference bằng **Kubernetes (AKS/EKS)**,  
CI/CD bằng **Azure DevOps Pipeline** hoặc **Jenkins/Travis CI**.

---

## 🎯 Mục tiêu
- Huấn luyện mô hình dự báo nhu cầu (XGBoost/Sklearn).
- Tự động build & deploy container model API lên cloud.
- CI/CD cho ML pipeline: build → test → train → register → deploy.
- So sánh triển khai trên **Azure (AML + AKS)** và **AWS (SageMaker + EKS)**.
- Expose API backend (FastAPI) cho ứng dụng khác sử dụng.

---

## 📂 Cấu trúc repo
```
retail-forecast/
├─ core/                 # Code ML Python chung (train, features, tests)
│   └─ requirements.txt
│
├─ server/               # Backend inference API (FastAPI)
│   ├─ app.py
│   ├─ Dockerfile
│   └─ requirements.txt
│
├─ azure/                # Cấu hình cho Azure
│   ├─ aml/              # Dockerfile + AML job
│   ├─ infra/            # main.bicep (IaC Azure)
│   ├─ k8s/              # deployment.yaml, service.yaml, hpa.yaml
│   └─ azure-pipelines.yml
│
├─ aws/                  # Cấu hình cho AWS
│   ├─ infra/            # Terraform EKS, ECR, S3
│   ├─ k8s/              # deployment.yaml, service.yaml, hpa.yaml
│   ├─ script/           # SageMaker train/register/deploy
│   ├─ Jenkinsfile       # CI/CD Jenkins
│   └─ .travis.yml       # CI/CD Travis (tuỳ chọn)
│
└─ README.md             # file này
```

---

## 🚀 Cách chạy nhanh

### 1. Core (train & test)
```bash
# Cài dependencies
pip install -r core/requirements.txt

# Train model (local)
python core/src/train.py --train_path ./data/train.csv --target quantity --out_dir ./artifacts

# Test
pytest core/tests
```

---

### 2. Backend API (local)
```bash
cd server
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# Gửi request thử
curl -X POST http://localhost:8000/predict   -H 'Content-Type: application/json'   -d '{"features": [[10,1,0],[12,0,1]]}'
```

---

### 3. Azure pipeline
- `azure/infra/main.bicep` → dựng hạ tầng (AKS, ACR).
- `azure/aml/train-job.yml` → định nghĩa job huấn luyện.
- `azure/k8s/*.yaml` → deploy app ML lên AKS.
- CI/CD: `azure-pipelines.yml`.

---

### 4. AWS pipeline
- `aws/infra/` → Terraform tạo EKS cluster, ECR repo, S3 buckets.
- `aws/k8s/*.yaml` → deploy app ML lên EKS (sử dụng image push từ server/).
- `aws/script/*.py` → train + register model trên SageMaker.
- CI/CD: `Jenkinsfile` hoặc `.travis.yml`.

---

## 🧩 Workflow tổng quan
1. **Code thay đổi (train.py/app.py)** → trigger CI/CD.
2. CI chạy **lint & test** (`pytest`, `flake8`).
3. CI gọi **SageMaker/Azure ML** để train → artifact model.
4. Model được **đăng ký** (SageMaker Registry hoặc AML).
5. Build Docker image inference (FastAPI) → push **ECR (AWS)** / **ACR (Azure)**.
6. Apply `k8s/` manifest → deploy API model lên **EKS (AWS)** / **AKS (Azure)**.
7. HPA auto-scale pods theo tải (CPU/memory).

---

## 📊 So sánh nhanh
| Thành phần       | Azure                                | AWS                                   |
|------------------|--------------------------------------|---------------------------------------|
| IaC              | Bicep                                | Terraform                             |
| Training         | Azure ML (AML job)                   | SageMaker Training Job                 |
| Model Registry   | AML Model Registry                   | SageMaker Model Registry               |
| Container Repo   | ACR                                  | ECR                                   |
| Orchestration    | AKS (Kubernetes)                     | EKS (Kubernetes)                       |
| CI/CD            | Azure DevOps Pipelines               | Jenkins / Travis CI                    |
| Monitoring       | Azure Monitor + Logs                 | CloudWatch                             |

---