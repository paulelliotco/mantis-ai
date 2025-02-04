import time
from contextlib import contextmanager
from typing import Dict, List
import logging


class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def measure(self, operation: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
            self.logger.debug(f"{operation} took {duration:.2f} seconds")
