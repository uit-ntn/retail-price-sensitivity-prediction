# 🛒 MLOps Azure – Retail Demand Forecast

## 📌 Giới thiệu
Dự án này triển khai **MLOps pipeline trên Azure** cho bài toán **dự báo nhu cầu bán lẻ (retail demand forecasting)**.  
Mục tiêu là xây dựng hệ thống **tự động huấn luyện, triển khai, và mở rộng mô hình ML** khi có thay đổi code hoặc dữ liệu.  

## 🏗️ Kiến trúc tổng quan
Pipeline bao gồm các thành phần chính:

- **Azure Pipelines** – CI/CD cho build, test, release mô hình.  
- **Azure Machine Learning (AML)** – huấn luyện, quản lý mô hình, đăng ký model.  
- **Azure Blob Storage** – lưu trữ dữ liệu huấn luyện và artifact model.  
- **Azure Container Registry (ACR)** – chứa Docker image cho train và inference.  
- **Azure Container Instances (ACI)** – môi trường DEV để deploy model nhanh.  
- **Azure Kubernetes Service (AKS)** – môi trường PROD cho deploy model scale lớn.  

## 📂 Cấu trúc thư mục
```
mlops-azure-retail-demand/
  src/
    train.py              # huấn luyện mô hình
    app.py                # inference API (FastAPI)
  aml/
    jobs/
      train-job.yml       # AML job cho huấn luyện
    environments/
      train.Dockerfile
      infer.Dockerfile
      conda.yml
  k8s/
    deployment.yaml
    service.yaml
    hpa.yaml
  infra/
    main.bicep            # IaC (hoặc Terraform)
  tests/
    test_train.py
  requirements.txt
  azure-pipelines.yml
  README.md
```

## 🚀 Cách chạy local
```bash
# Tạo env
python -m venv .venv
source .venv/bin/activate   # hoặc .venv\Scripts\activate trên Windows

# Cài thư viện
pip install -r requirements.txt

# Chạy huấn luyện local
python src/train.py --data ./data --out_dir ./outputs --epochs 5

# Chạy inference local
uvicorn src.app:app --reload --port 8000
```

Mở trình duyệt: [http://127.0.0.1:8000/predict?qty=100](http://127.0.0.1:8000/predict?qty=100)

---

## 🧪 Test
```bash
pytest -q
```

---

## ⚙️ CI/CD Flow
1. **CI**: Build & push Docker images → ACR  
2. **CD**: Submit training job trên AML → Đăng ký model  
3. **Deploy DEV**: Triển khai inference API trên ACI  
4. **Deploy PROD**: Deploy model trên AKS + autoscale (HPA)  

---

## 📈 Roadmap
- [x] Tạo repo + skeleton  
- [ ] Viết train script đầy đủ (real dataset)  
- [ ] Thiết lập Azure Pipelines  
- [ ] Tích hợp Azure ML training  
- [ ] Triển khai DEV trên ACI  
- [ ] Triển khai PROD trên AKS  
- [ ] Monitoring & retraining automation  

---
