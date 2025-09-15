from fastapi import FastAPI
import pickle
import os

app = FastAPI()

# Load model khi container start
MODEL_PATH = os.getenv("MODEL_PATH", "./outputs/model.pkl")

model = None
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print(f"[INFO] Loaded model from {MODEL_PATH}")
else:
    print("[WARNING] No model found, running in dummy mode")


@app.get("/predict")
def predict(qty: int):
    """
    Fake predict function – dự báo nhu cầu dựa vào qty nhập vào
    """
    if model:
        # Giả lập inference: nhân qty với số epochs để ra kết quả
        forecast = qty * model.get("epochs", 1) * 1.1
        return {"input_qty": qty, "forecast": forecast, "model_info": model}
    else:
        # Nếu chưa có model.pkl thì trả về kết quả dummy
        return {"input_qty": qty, "forecast": qty * 1.2, "model_info": "dummy"}


# Dùng uvicorn để chạy: uvicorn src.app:app --reload --port 8000
