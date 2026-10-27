"""
Streamlit Root Application Launcher.

Allows running the dashboard directly from root using either:
    python -m streamlit run app.py
or
    python -m streamlit run src/app.py
"""

import os
import sys
import runpy

# Ensure project root is in Python sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

target_script = os.path.join(PROJECT_ROOT, "src", "app.py")
runpy.run_path(target_script, run_name="__main__")
