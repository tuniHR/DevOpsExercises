import http.server
import socketserver
import subprocess
import json
import requests
import os
from datetime import datetime

PORT = 8199


# Log file location
LOG_FILE = "/app/log/log-file.txt"
STATUS_FILE = "/app/log/status.txt" 


def log_state_change(old_state, new_state):
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    log_entry = f"{timestamp}: {old_state}->{new_state}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)

def update_status(new_state):
    with open(STATUS_FILE, 'w') as f:
        f.write(new_state + '\n')

def get_current_state():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            state = f.readline().strip()
            return state
    return "INIT"

update_status("INIT")
with open(LOG_FILE, 'w') as f:
    f.write("")

class CustomHandler(http.server.SimpleHTTPRequestHandler):


    def do_GET(self):
        current_state = get_current_state()

        if current_state == "PAUSED":
            self.send_response(503)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("".encode('utf-8'))
            return
        # Handle GET requests for state and logs
        if self.path == "/state":
            # Return the current state as plain text
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(current_state.encode('utf-8'))

        elif self.path == "/run-log":
            # Return the contents of the log file as plain text
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    log_contents = f.read()
                self.wfile.write(log_contents.encode('utf-8'))
            else:
                self.wfile.write("No logs available yet.".encode('utf-8'))

        elif self.path == "/request":
            # Example: Info about Service1 and Service2
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "Service1": self.get_service1_info(),
                "Service2": self.get_service2_info()
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_PUT(self):
        if self.path == "/state":
            # Parse the payload and set the state
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            new_state = body.decode('utf-8').strip()

            # Validate new state
            if new_state not in ['INIT', 'PAUSED', 'RUNNING', 'SHUTDOWN']:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                response = "Invalid state"
                self.wfile.write(response.encode('utf-8'))
                return

            # Ensure state transitions only happen if the state is different
            current_state = get_current_state()
            if new_state != current_state:
                # Log the state change before updating it
                log_state_change(current_state, new_state)
                update_status(new_state)

            

            # Update the current state
            current_state = new_state
            
            # Handle actions based on the new state
            if current_state == 'SHUTDOWN':
                # Trigger shutdown of containers (example, you may handle differently)
                self.shutdown_containers()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            response = f"State changed to {new_state}"
            self.wfile.write(response.encode('utf-8'))

        else:
            # Handle unsupported PUT request
            self.send_response(405)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            response = "Method Not Allowed"
            self.wfile.write(response.encode('utf-8'))

    def do_POST(self):
        current_state = get_current_state()

        if current_state == "PAUSED":
            self.send_response(503)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("".encode('utf-8'))
            return

        if self.path == "/login":
            
            if current_state == "INIT":
                update_status("RUNNING")
                log_state_change(current_state, "RUNNING")

                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                response = f"State changed to RUNNING"
                self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(405)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            response = "Something went wrong"
            self.wfile.write(response.encode('utf-8'))


    def get_service1_info(self):
        # Gather system information about Service1
        return {
            "IP address": subprocess.getoutput("hostname -I").strip(),
            "Running processes": subprocess.getoutput("ps -ax"),
            "Available disk space": subprocess.getoutput("df -h /"),
            "Time since last boot": subprocess.getoutput("uptime -p")
        }
    
    def get_service2_info(self):
        # Fetch information from Service2
        try:
            response = requests.get('http://service2:8200')
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def shutdown_containers(self):
        # Example: Request to Service2 to stop containers
        try:
            response = requests.post('http://service2:8200/stop')
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Set up the HTTP server
Handler = CustomHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
