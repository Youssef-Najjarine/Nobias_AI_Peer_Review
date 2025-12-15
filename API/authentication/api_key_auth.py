# API/authentication/api_key_auth.py
from fastapi import Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

# Change this in production! Use environment variable.
API_KEY = "nobias-secret-key-2025"  # Replace with os.getenv("NOBIAS_API_KEY")
API_KEY_NAME = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: str = Security(API_KEY_NAME)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key",
        )
    return api_key