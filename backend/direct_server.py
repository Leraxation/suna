#!/usr/bin/env python3
"""
Direct server that runs the FastAPI app without importing asyncio directly
"""
import sys
import os
import subprocess

# Set environment variables to avoid asyncio conflicts
os.environ['DISABLE_UVLOOP'] = '1'
os.environ['PYTHONPATH'] = '/app'

def main():
    """Run the FastAPI app using python -m uvicorn directly"""
    try:
        # Use python -m uvicorn to run the app
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'api:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--workers', '1',
            '--loop', 'asyncio',
            '--log-level', 'info'
        ]
        
        print(f"Starting FastAPI server with command: {' '.join(cmd)}")
        
        # Run the server
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Server failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Server stopped")

if __name__ == '__main__':
    main()