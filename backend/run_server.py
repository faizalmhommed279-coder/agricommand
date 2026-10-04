import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    print("AgriCommand Server starting on http://127.0.0.1:8000 ...", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
