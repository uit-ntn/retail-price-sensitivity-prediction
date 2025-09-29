import json, os, joblib, glob
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

MODEL_DIR = "/opt/ml/processing/model"
TEST_DIR  = "/opt/ml/processing/test"
OUT_DIR   = "/opt/ml/processing/metrics"

def load_model():
    model_path = glob.glob(os.path.join(MODEL_DIR, "**", "*.pkl"), recursive=True)
    if not model_path:
        model_path = glob.glob(os.path.join(MODEL_DIR, "*.tar.gz"))
        # if tar.gz, you could extract then load
    return joblib.load(model_path[0])

def load_test():
    # Expect two files: X.npy, y.npy
    X = np.load(os.path.join(TEST_DIR, "X.npy"))
    y = np.load(os.path.join(TEST_DIR, "y.npy"))
    return X, y

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    model = load_model()
    X, y = load_test()
    y_pred = model.predict(X)
    metrics = {
        "regression_metrics": {
            "mse": float(mean_squared_error(y, y_pred)),
            "r2":  float(r2_score(y, y_pred))
        }
    }
    with open(os.path.join(OUT_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f)
    print("Wrote metrics.json:", metrics)

if __name__ == "__main__":
    main()
