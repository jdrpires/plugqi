from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# In a real scenario, this would come from a Database


# Securely load keys from Environment Variables
# Format: { "api_key": "client_name" }
# Dynamic Loading: Any env var starting with PLUGQI_CLIENT_ is treated as a client key
VALID_API_KEYS = {}

# 1. Load Fallback/Dev Key
if os.environ.get("PLUGQI_API_KEY"):
    VALID_API_KEYS[os.environ.get("PLUGQI_API_KEY")] = "Default Client"

# 2. Dynamic Discovery
for env_var, value in os.environ.items():
    if env_var.startswith("PLUGQI_CLIENT_"):
        # Example: PLUGQI_CLIENT_PECA_RARA -> Peca Rara
        client_name = env_var.replace("PLUGQI_CLIENT_", "").replace("_", " ").title()
        VALID_API_KEYS[value] = client_name

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """
    Validates API Key and returns the Client Name.
    """
    if api_key_header in VALID_API_KEYS:
        # We can return the client info here to be used in endpoints
        return {
            "client": VALID_API_KEYS[api_key_header],
            "key": api_key_header
        }
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )
