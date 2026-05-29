"""
Simple HTTP Server for JARVIS Frontend
Serves the web dashboard on http://localhost:8000
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 8000
WEB_DIR = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{self.client_address[0]}] {format % args}")

def start_server():
    """Start HTTP server"""
    os.chdir(WEB_DIR)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"""
╔═══════════════════════════════════════════╗
║       JARVIS Web Dashboard Server         ║
╚═══════════════════════════════════════════╝

📡 Server running at: http://localhost:{PORT}
📁 Serving from: {WEB_DIR}

🔗 Open in browser:
   • http://localhost:{PORT}
   • http://127.0.0.1:{PORT}

⚠️  Make sure backend server is running:
   cd backend && python server.py

Press Ctrl+C to stop server
""")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
            sys.exit(0)

if __name__ == "__main__":
    start_server()
