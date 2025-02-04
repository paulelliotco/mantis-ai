from typing import List, Dict, Union
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

class BatchProcessor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    def process_batch(
        self, 
        files: List[Union[str, Path]], 
        operation: str,
        **kwargs
    ) -> Dict[str, Any]:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            if operation == "transcribe":
                futures = {executor.submit(transcribe, str(f)): f for f in files}
            elif operation == "summarize":
                futures = {executor.submit(summarize, str(f)): f for f in files}
            elif operation == "extract":
                futures = {executor.submit(extract, str(f), kwargs.get("prompt", "")): f for f in files}
            
            results = {}
            for future in futures:
                file = futures[future]
                try:
                    results[str(file)] = future.result()
                except Exception as e:
                    results[str(file)] = {"error": str(e)}
            
            return results