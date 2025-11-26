"""
Health Check Script for Docker HEALTHCHECK
Checks if the FastAPI application is responding correctly
"""

import sys
import httpx

def check_health():
    """Check if API health endpoint is responding"""
    try:
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                sys.exit(0)  # Healthy
        
        sys.exit(1)  # Unhealthy
        
    except Exception:
        sys.exit(1)  # Unhealthy

if __name__ == "__main__":
    check_health()
