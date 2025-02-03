import importlib.util
import os
from unittest.mock import patch
import sys  # Add this import

spec = importlib.util.spec_from_file_location("mantis.summarize", os.path.join("mantis", "summarize.py"))
summarize_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summarize_module)
sys.modules["mantis.summarize"] = summarize_module  # Override sys.modules entry

# ... the rest of your test code remains as is
