"""
Vercel Serverless Function Entrypoint
FastAPI ASGI handler for AI Resume Analyzer & Job Matching Agent
"""
import os
import sys

# Ensure repository root is on sys.path for importing local modules
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

# Import the FastAPI application
from resume_analyzer import app

# Export app as required by Vercel's Python runtime
__all__ = ["app"]
