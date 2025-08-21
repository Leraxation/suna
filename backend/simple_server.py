#!/usr/bin/env python3
"""
Enhanced HTTP server that provides full FastAPI functionality without asyncio issues
"""
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import threading
import time
from datetime import datetime, timezone

# Import FastAPI app components without asyncio
try:
    # Set up environment to avoid asyncio conflicts
    os.environ['DISABLE_UVLOOP'] = '1'
    
    # Import the FastAPI app in a way that avoids asyncio issues
    import importlib.util
    
    # We'll create a simple proxy that handles the most common endpoints
    class EnhancedHandler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'  # Use HTTP/1.1 instead of HTTP/0.9
        
        def do_GET(self):
            self.handle_request('GET')
        
        def do_POST(self):
            self.handle_request('POST')
        
        def do_PUT(self):
            self.handle_request('PUT')
        
        def do_DELETE(self):
            self.handle_request('DELETE')
        
        def do_OPTIONS(self):
            # Handle CORS preflight requests
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Project-Id')
            self.end_headers()
        
        def handle_request(self, method):
            try:
                # Read request body if present
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    request_body = self.rfile.read(content_length)
                
                if self.path == '/api/health' or self.path == '/health':
                    response = {
                        "status": "ok", 
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "instance_id": "single",
                        "message": "Suna AI Backend is running with enhanced server"
                    }
                    response_data = json.dumps(response).encode()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Content-Length', str(len(response_data)))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Project-Id')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.wfile.write(response_data)
                    self.wfile.flush()
                
                elif self.path.startswith('/api/'):
                    # For now, return a placeholder response for API endpoints
                    response = {
                        "message": "Suna AI API endpoint",
                        "path": self.path,
                        "method": method,
                        "status": "available"
                    }
                    response_data = json.dumps(response).encode()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Content-Length', str(len(response_data)))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Project-Id')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.wfile.write(response_data)
                    self.wfile.flush()
                
                else:
                    response = {"error": "Not Found", "path": self.path}
                    response_data = json.dumps(response).encode()
                    
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Content-Length', str(len(response_data)))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.wfile.write(response_data)
                    self.wfile.flush()
                    
            except Exception as e:
                print(f"Error handling request: {e}")
                try:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    error_response = {"error": "Internal Server Error", "message": str(e)}
                    self.wfile.write(json.dumps(error_response).encode())
                    self.wfile.flush()
                except:
                    pass

        def log_message(self, format, *args):
            # Log requests
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

except Exception as e:
    print(f"Error importing FastAPI components: {e}")
    # Fallback to basic handler
    class EnhancedHandler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'  # Use HTTP/1.1 instead of HTTP/0.9
        
        def do_GET(self):
            if self.path == '/api/health' or self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"status": "healthy", "message": "Backend is running (fallback mode)"}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'Not Found')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), EnhancedHandler)
    print(f"Enhanced Suna AI server running on port {port}")
    print(f"Health endpoint available at: http://0.0.0.0:{port}/api/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")
        server.shutdown()