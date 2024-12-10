#!/bin/bash

BASE_URL="http://localhost:8197"

# Test GET /state without authentication
test_get_state_no_auth() {
    echo "Testing GET /state without authentication"
    response=$(curl -s -w "%{http_code}" -o response.txt "$BASE_URL/state")
    status_code="${response: -3}"
    response_body=$(cat response.txt)

    if [ "$status_code" -eq 200 ] && [[ "$response_body" == "INIT" || "$response_body" == "PAUSED" || "$response_body" == "RUNNING" || "$response_body" == "SHUTDOWN" ]]; then
        echo "GET /state test passed"
    else
        echo "GET /state test failed"
        exit 1
    fi
}

# Test PUT /state without authentication
test_put_state_no_auth() {
    echo "Testing PUT /state without authentication"
    response=$(curl -s -w "%{http_code}" -o response.txt -X PUT -d "RUNNING" "$BASE_URL/state")
    status_code="${response: -3}"

    if [ "$status_code" -eq 401 ]; then
        echo "PUT /state without authentication test passed"
    else
        echo "PUT /state without authentication test failed"
        exit 1
    fi
}

# Test PUT /state with authentication (admin:admin)
test_put_state_auth() {
    echo "Testing PUT /state with authentication"
    response=$(curl -s -w "%{http_code}" -o response.txt -X PUT -d "RUNNING" -u "admin:admin" "$BASE_URL/state")
    status_code="${response: -3}"
    response_body=$(cat response.txt)

    if [ "$status_code" -eq 200 ] && [[ "$response_body" == "State changed to RUNNING" ]]; then
        echo "PUT /state with authentication test passed"
    else
        echo "PUT /state with authentication test failed"
        exit 1
    fi
}

# Test PUT /state to PAUSED and check if /request is not accessible
test_put_pause() {
    echo "Testing PUT /state to PAUSED"
    response=$(curl -s -w "%{http_code}" -o response.txt -X PUT -d "PAUSED" -u "admin:admin" "$BASE_URL/state")
    status_code="${response: -3}"
    response_body=$(cat response.txt)

    if [ "$status_code" -eq 200 ] && [[ "$response_body" == "State changed to PAUSED" ]]; then
        echo "PUT /state to PAUSED test passed"
    else
        echo "PUT /state to PAUSED test failed"
        exit 1
    fi

    echo "Testing GET /request after PAUSED"
    response=$(curl -s -w "%{http_code}" -o response.txt "$BASE_URL/request")
    status_code="${response: -3}"

    if [ "$status_code" -ne 200 ]; then
        echo "GET /request after PAUSED test passed"
    else
        echo "GET /request after PAUSED test failed"
        exit 1
    fi

    # Put back to running state
    echo "Putting back to RUNNING state"
    response=$(curl -s -w "%{http_code}" -o response.txt -X PUT -d "RUNNING" -u "admin:admin" "$BASE_URL/state")
    status_code="${response: -3}"

    if [ "$status_code" -eq 200 ]; then
        echo "State changed back to RUNNING"
    else
        echo "Failed to change state back to RUNNING"
        exit 1
    fi
}

# Test GET /request
test_get_request() {
    echo "Testing GET /request"
    response=$(curl -s -w "%{http_code}" -o response.txt "$BASE_URL/request")
    status_code="${response: -3}"

    if [ "$status_code" -eq 200 ]; then
        echo "GET /request test passed"
    else
        echo "GET /request test failed"
        exit 1
    fi
}

# Test GET /run-log
test_get_run_log() {
    echo "Testing GET /run-log"
    
    # First set state to INIT and then to RUNNING
    response=$(curl -s -w "%{http_code}" -o response.txt -X PUT -d "INIT" -u "admin:admin" "$BASE_URL/state")
    status_code="${response: -3}"
    
    response=$(curl -s -w "%{http_code}" -o response.txt -X PUT -d "RUNNING" -u "admin:admin" "$BASE_URL/state")
    status_code="${response: -3}"

    # Now test the /run-log endpoint
    response=$(curl -s -w "%{http_code}" -o response.txt "$BASE_URL/run-log")
    status_code="${response: -3}"
    response_body=$(cat response.txt)

    if [ "$status_code" -eq 200 ] && [[ "$response_body" == *"RUNNING"* ]]; then
        echo "GET /run-log test passed"
    else
        echo "GET /run-log test failed"
        exit 1
    fi
}

# Run all tests
test_get_state_no_auth
test_put_state_no_auth
test_put_state_auth
test_put_pause
test_get_request
test_get_run_log

echo "All tests passed!"
