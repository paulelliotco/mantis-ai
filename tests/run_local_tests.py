#!/usr/bin/env python3
import os
import sys
import pytest

def main():
    # Set environment variables for local testing
    os.environ["LOCAL_TEST"] = "true"
    
    # Ensure GEMINI_API_KEY is set
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set")
        sys.exit(1)

    # Run tests with local_only marker
    pytest.main(["-v", "-m", "local_only"])

if __name__ == "__main__":
    main()