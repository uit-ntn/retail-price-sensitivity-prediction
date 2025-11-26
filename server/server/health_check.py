"""
Health check script for Docker HEALTHCHECK
"""
import sys
import httpx

def check_health():
    try:
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                sys.exit(0)
        sys.exit(1)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    check_health()
