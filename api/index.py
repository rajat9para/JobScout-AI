"""Vercel serverless entry point.

Exports the FastAPI ASGI app for Vercel's @vercel/python runtime.
All routes from app.main are automatically available.
"""
import sys
import os

# Ensure the project root is in the Python path so 'app' package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Vercel expects the ASGI app to be named 'app' or 'handler'
# FastAPI is ASGI-native, so this works directly.
