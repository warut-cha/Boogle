import sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from ai_engine.bob_client import BobClient
    print("BobClient loaded successfully")
except Exception as e:
    print(f"Error: {e}")
