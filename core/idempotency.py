from fastapi import Request, HTTPException
from starlette.status import HTTP_409_CONFLICT
from typing import Set
import threading

# In-memory store for demonstration; replace with persistent store in production
_idempotency_keys: Set[str] = set()
_lock = threading.Lock()

async def idempotency_key_dependency(request: Request):
    key = request.headers.get("Idempotency-Key")
    if not key:
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key header")
    with _lock:
        if key in _idempotency_keys:
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail="Duplicate request: Idempotency-Key already used")
        _idempotency_keys.add(key)
    # Optionally: clean up old keys after some time
    return key
