#!/bin/bash
#
# HTTP Client Utility for Integration Tests
#
# Provides common HTTP request functions with proper error handling,
# timeout management, and response validation for testing APIs.
#

# Default configuration
readonly DEFAULT_TIMEOUT=10
readonly DEFAULT_RETRIES=3
readonly DEFAULT_RETRY_DELAY=2

# HTTP request function with timeout and retries
http_request() {
    local method="$1"
    local url="$2"
    local data="${3:-}"
    local headers="${4:-}"
    local timeout="${5:-$DEFAULT_TIMEOUT}"
    local retries="${6:-$DEFAULT_RETRIES}"
    
    local attempt=1
    local response_file=$(mktemp)
    local http_code_file=$(mktemp)
    
    # Cleanup temporary files on exit
    trap "rm -f ${response_file} ${http_code_file}" RETURN
    
    while [[ $attempt -le $retries ]]; do
        local curl_args=(
            --max-time "$timeout"
            --connect-timeout 5
            --silent
            --show-error
            --location
            --write-out "%{http_code}"
            --output "$response_file"
        )
        
        # Add method
        if [[ "$method" != "GET" ]]; then
            curl_args+=("--request" "$method")
        fi
        
        # Add headers if provided
        if [[ -n "$headers" ]]; then
            while IFS='|' read -ra HEADER_ARRAY; do
                for header in "${HEADER_ARRAY[@]}"; do
                    curl_args+=("--header" "$header")
                done
            done <<< "$headers"
        fi
        
        # Add data for POST/PUT requests
        if [[ -n "$data" && ("$method" == "POST" || "$method" == "PUT" || "$method" == "PATCH") ]]; then
            curl_args+=("--data" "$data")
        fi
        
        # Add URL
        curl_args+=("$url")
        
        # Execute request
        local http_code
        if http_code=$(curl "${curl_args[@]}" 2>"$http_code_file"); then
            # Success - return response and status code
            echo "HTTP_CODE:$http_code"
            echo "RESPONSE:$(cat "$response_file")"
            return 0
        else
            local curl_exit_code=$?
            local error_message=$(cat "$http_code_file" 2>/dev/null || echo "Unknown error")
            
            if [[ $attempt -eq $retries ]]; then
                echo "HTTP_CODE:000"
                echo "ERROR:Request failed after $retries attempts. Last error: $error_message (curl exit code: $curl_exit_code)"
                return 1
            fi
            
            echo "Attempt $attempt failed, retrying in ${DEFAULT_RETRY_DELAY}s..." >&2
            sleep $DEFAULT_RETRY_DELAY
            ((attempt++))
        fi
    done
}

# GET request wrapper
http_get() {
    local url="$1"
    local headers="${2:-}"
    local timeout="${3:-$DEFAULT_TIMEOUT}"
    
    http_request "GET" "$url" "" "$headers" "$timeout"
}

# POST request wrapper
http_post() {
    local url="$1"
    local data="$2"
    local headers="${3:-Content-Type: application/json}"
    local timeout="${4:-$DEFAULT_TIMEOUT}"
    
    http_request "POST" "$url" "$data" "$headers" "$timeout"
}

# PUT request wrapper
http_put() {
    local url="$1"
    local data="$2"
    local headers="${3:-Content-Type: application/json}"
    local timeout="${4:-$DEFAULT_TIMEOUT}"
    
    http_request "PUT" "$url" "$data" "$headers" "$timeout"
}

# DELETE request wrapper
http_delete() {
    local url="$1"
    local headers="${2:-}"
    local timeout="${3:-$DEFAULT_TIMEOUT}"
    
    http_request "DELETE" "$url" "" "$headers" "$timeout"
}

# HTTP OPTIONS request (for CORS testing)
http_options() {
    local url="$1"
    local headers="$2"
    local timeout="${3:-$DEFAULT_TIMEOUT}"
    
    http_request "OPTIONS" "$url" "" "$headers" "$timeout"
}

# Parse response from http_request output
parse_http_response() {
    local response_text="$1"
    local field="$2"  # HTTP_CODE, RESPONSE, or ERROR
    
    echo "$response_text" | grep "^${field}:" | cut -d':' -f2-
}

# Check if response status code indicates success
is_success_status() {
    local status_code="$1"
    [[ "$status_code" -ge 200 && "$status_code" -lt 300 ]]
}

# Check if response status code indicates client error
is_client_error() {
    local status_code="$1"
    [[ "$status_code" -ge 400 && "$status_code" -lt 500 ]]
}

# Check if response status code indicates server error
is_server_error() {
    local status_code="$1"
    [[ "$status_code" -ge 500 && "$status_code" -lt 600 ]]
}

# Health check wrapper with service-specific logic
check_service_health() {
    local service_name="$1"
    local port="$2"
    local health_endpoint="${3:-/health}"
    local timeout="${4:-5}"
    
    local url="http://localhost:${port}${health_endpoint}"
    local response=$(http_get "$url" "" "$timeout")
    local status_code=$(parse_http_response "$response" "HTTP_CODE")
    local response_body=$(parse_http_response "$response" "RESPONSE")
    
    if is_success_status "$status_code"; then
        echo "SUCCESS:$service_name is healthy"
        return 0
    else
        local error_msg=$(parse_http_response "$response" "ERROR")
        echo "FAILED:$service_name health check failed (HTTP $status_code): ${error_msg:-$response_body}"
        return 1
    fi
}

# Test API endpoint with expected response validation
test_api_endpoint() {
    local method="$1"
    local url="$2"
    local expected_status="$3"
    local data="${4:-}"
    local headers="${5:-}"
    local timeout="${6:-$DEFAULT_TIMEOUT}"
    
    local response
    case "$method" in
        "GET")
            response=$(http_get "$url" "$headers" "$timeout")
            ;;
        "POST")
            response=$(http_post "$url" "$data" "$headers" "$timeout")
            ;;
        "PUT")
            response=$(http_put "$url" "$data" "$headers" "$timeout")
            ;;
        "DELETE")
            response=$(http_delete "$url" "$headers" "$timeout")
            ;;
        *)
            echo "ERROR:Unsupported HTTP method: $method"
            return 1
            ;;
    esac
    
    local actual_status=$(parse_http_response "$response" "HTTP_CODE")
    local response_body=$(parse_http_response "$response" "RESPONSE")
    
    if [[ "$actual_status" == "$expected_status" ]]; then
        echo "SUCCESS:$method $url returned expected status $expected_status"
        echo "RESPONSE:$response_body"
        return 0
    else
        local error_msg=$(parse_http_response "$response" "ERROR")
        echo "FAILED:$method $url expected status $expected_status, got $actual_status"
        echo "ERROR:${error_msg:-$response_body}"
        return 1
    fi
}

# Wait for service to be ready with exponential backoff
wait_for_service() {
    local service_name="$1"
    local port="$2"
    local max_attempts="${3:-30}"
    local health_endpoint="${4:-/health}"
    
    local attempt=1
    local delay=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if check_service_health "$service_name" "$port" "$health_endpoint" 2 >/dev/null; then
            echo "SUCCESS:$service_name is ready after $attempt attempts"
            return 0
        fi
        
        echo "Waiting for $service_name (attempt $attempt/$max_attempts)..." >&2
        sleep $delay
        
        # Exponential backoff with maximum delay of 8 seconds
        if [[ $delay -lt 8 ]]; then
            delay=$((delay * 2))
        fi
        
        ((attempt++))
    done
    
    echo "FAILED:$service_name did not become ready after $max_attempts attempts"
    return 1
}