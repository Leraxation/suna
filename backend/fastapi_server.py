#!/usr/bin/env python3
"""
FastAPI server using gunicorn to avoid asyncio conflicts
"""
import os
import sys
import subprocess

def main():
    """Run the FastAPI app with gunicorn"""
    # Set environment variables to disable uvloop and other asyncio optimizations
    os.environ['DISABLE_UVLOOP'] = '1'
    os.environ['PYTHONPATH'] = '/app'
    
    # Run gunicorn with the FastAPI app
    cmd = [
        'gunicorn',
        'api:app',
        '--bind', '0.0.0.0:8000',
        '--workers', '1',
        '--worker-class', 'uvicorn.workers.UvicornWorker',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--log-level', 'info'
    ]
    
    print(f"Starting FastAPI server with command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Server failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Server stopped")

if __name__ == '__main__':
    main()