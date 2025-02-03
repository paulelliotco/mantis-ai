import importlib.util
import os
from unittest.mock import patch
import sys  # Add this import

spec = importlib.util.spec_from_file_location("mantis.extract", os.path.join("mantis", "extract.py"))
extract_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract_module)
sys.modules["mantis.extract"] = extract_module  # Override sys.modules entry

# ... your test classes and methods that use extract_module.extract(...)
