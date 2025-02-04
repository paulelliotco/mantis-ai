import hashlib
import json
from pathlib import Path
from typing import Optional, Any
from diskcache import Cache

class ResultCache:
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache = Cache(cache_dir or Path.home() / ".mantis" / "cache")
    
    def get_key(self, audio_file: str, operation: str, **kwargs) -> str:
        """Generate a unique cache key based on input parameters"""
        params = {"file": audio_file, "op": operation, **kwargs}
        return hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, expire: int = 86400) -> None:
        self.cache.set(key, value, expire=expire)