# run_api.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "API.rest_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )