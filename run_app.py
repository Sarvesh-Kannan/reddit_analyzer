#!/usr/bin/env python3
"""
Launcher for Indian Fashion Trend Analysis App
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit app"""
    print("🇮🇳 Indian Fashion Trend Analysis")
    print("="*50)
    print("Starting Streamlit application...")
    print("Dashboard will be available at: http://localhost:8501")
    print("="*50)
    
    try:
        # Run streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {str(e)}")

if __name__ == "__main__":
    main() 