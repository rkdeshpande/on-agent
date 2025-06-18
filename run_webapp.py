#!/usr/bin/env python3
import sys
from pathlib import Path

from app.webapp import app

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
