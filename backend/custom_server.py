#!/usr/bin/env python3
"""
Custom server that runs the FastAPI app directly without uvicorn
"""
import asyncio
import sys
import os
from hypercorn.config import Config
from hypercorn.asyncio import serve

# Set environment variables to avoid asyncio conflicts
os.environ['DISABLE_UVLOOP'] = '1'
os.environ['PYTHONPATH'] = '/app'

async def main():
    """Run the FastAPI app with hypercorn directly"""
    try:
        # Import the FastAPI app
        from api import app
        
        # Configure hypercorn
        config = Config()
        config.bind = ["0.0.0.0:8000"]
        config.workers = 1
        config.access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
        config.accesslog = "-"
        config.errorlog = "-"
        
        print(f"Starting FastAPI server with hypercorn on 0.0.0.0:8000")
        
        # Run the server
        await serve(app, config)
        
    except Exception as e:
        print(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Set Windows event loop policy if on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")