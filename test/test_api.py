import requests
from requests.auth import HTTPBasicAuth
import pytest

BASE_URL = "http://localhost:8197" 

# Test for GET /state without authentication
def test_get_state_no_auth():
    response = requests.get(f"{BASE_URL}/state")
    assert response.status_code == 200
    assert response.text in ["INIT", "PAUSED", "RUNNING", "SHUTDOWN"]

# Test for PUT /state without authentication
def test_put_state_no_auth():
    response = requests.put(f"{BASE_URL}/state", data="RUNNING")
    assert response.status_code == 401  # Unauthorized

# Test for PUT /state with authentication (admin:password)
def test_put_state_auth():
    response = requests.put(
        f"{BASE_URL}/state", 
        data="RUNNING", 
        auth=HTTPBasicAuth("admin", "admin")
    )
    assert response.status_code == 200
    

# Test for GET /request
def test_get_request():
    response = requests.get(f"{BASE_URL}/request")
    assert response.status_code == 200
    

# Test for GET /run-log
def test_get_run_log():
    response = requests.get(f"{BASE_URL}/run-log")
    assert response.status_code == 200
    
