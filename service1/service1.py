import http.server
import socketserver
import subprocess
import json
import requests

PORT = 8199

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "Service1": self.get_service1_info(),
            "Service2": self.get_service2_info()
        
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def get_service1_info(self):
        return {
            "IP address": subprocess.getoutput("hostname -I").strip(),
            "Running processes": subprocess.getoutput("ps -ax"),
            "Available disk space": subprocess.getoutput("df -h /"),
            "Time since last boot": subprocess.getoutput("uptime -p")
        }
    
    def get_service2_info(self):
        try:
            response = requests.get('http://service2:8200')
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
Handler = CustomHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()