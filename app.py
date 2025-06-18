from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORS
from cachetools import TTLCache
import lib2
import json
from functools import wraps

app = FastAPI()
CORS(app, allow_origins=["*"])
cache = TTLCache(maxsize=100, ttl=300)

def cached_endpoint(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = (request.path, tuple(request.query_params.items()))
            if cache_key in cache:
                return cache[cache_key]
            result = await func(*args, **kwargs)
            cache[cache_key] = result
            return result
        return wrapper
    return decorator

@app.get("/api/account")
@cached_endpoint()
async def get_account_info(uid: str, region: str):
    if not uid:
        raise HTTPException(400, detail={"error": "Invalid request", "message": "Empty 'uid' parameter."})
    if not region:
        raise HTTPException(400, detail={"error": "Invalid request", "message": "Empty 'region' parameter."})
    try:
        return_data = await lib2.GetAccountInformation(uid, "7", region, "/GetPlayerPersonalShow")
        return return_data
    except Exception as e:
        raise HTTPException(500, detail={"error": "Server error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
