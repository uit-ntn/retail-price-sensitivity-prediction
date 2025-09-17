# Server (Inference API)
FastAPI phục vụ dự đoán, chạy trong container và deploy lên K8s (AKS/EKS).

## Biến môi trường
- `S3_MODEL_BUCKET`, `S3_MODEL_KEY`, `AWS_REGION` — tải model từ S3 **(khuyên dùng)**.
- `MODEL_LOCAL_PATH` — nếu bundle model trong image (mặc định `/app/model/model.joblib`).

## Chạy local
```bash
export S3_MODEL_BUCKET=your-bucket
export S3_MODEL_KEY=path/to/model.joblib
export AWS_REGION=ap-southeast-1
uvicorn server.app:app --reload --port 8000
