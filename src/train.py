import argparse
import os
import pickle
import mlflow


def train(data_path: str, out_dir: str, epochs: int):
    """
    Fake training function – giả lập huấn luyện model
    """
    print(f"[INFO] Training model with data from {data_path} for {epochs} epochs")

    # log params & metrics vào MLflow (Azure ML tự tích hợp MLflow)
    mlflow.log_param("epochs", epochs)
    mlflow.log_metric("mae", 12.3)   # giả lập metric
    mlflow.log_metric("rmse", 20.5)

    # Tạo output folder nếu chưa có
    os.makedirs(out_dir, exist_ok=True)

    # Giả lập model object
    model = {"name": "retail-forecast-model", "version": "0.0.1", "epochs": epochs}

    # Lưu model dưới dạng pickle
    model_path = os.path.join(out_dir, "model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    print(f"[INFO] Model saved to {model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="Path to training data")
    parser.add_argument("--out_dir", type=str, default="./outputs", help="Output directory")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    args = parser.parse_args()

    train(args.data, args.out_dir, args.epochs)
