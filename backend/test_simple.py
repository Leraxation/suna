#!/usr/bin/env python3
"""
Simple test script to check if FastAPI can run without complex dependencies
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Simple Test API")

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "simple-test"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Simple test API is running"}

if __name__ == "__main__":
    print("Starting simple test server...")
    uvicorn.run(
        "test_simple:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )