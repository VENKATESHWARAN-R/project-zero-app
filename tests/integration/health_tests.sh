#!/bin/bash
#
# Health Check Tests for Project Zero App Services
#
# Tests all 9 services to verify they respond to /health endpoints
# with proper status codes and response formats.
#

set -euo pipefail

# Source utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../utils/http_client.sh"
source "${SCRIPT_DIR}/../utils/validate_response.sh"
source "${SCRIPT_DIR}/../utils/test_reporter.sh"

# Service configuration
declare -A SERVICES=(
    ["auth-service"]="8001"
    ["user-profile-service"]="8002"
    ["product-service"]="8004"
    ["cart-service"]="8007"
    ["order-service"]="8008"
    ["payment-service"]="8009"
    ["notification-service"]="8011"
    ["api-gateway"]="8000"
)

# Test configuration
readonly HEALTH_ENDPOINT="/health"
readonly TIMEOUT=10
readonly MAX_RETRIES=3

# Initialize reporting
init_reporting

# Test individual service health endpoint
test_service_health() {
    local service_name="$1"
    local port="$2"
    
    local start_time=$(date +%s)
    
    echo "Testing $service_name health endpoint..."
    
    local response=$(http_get "http://localhost:${port}${HEALTH_ENDPOINT}" "" "$TIMEOUT")
    local status_code=$(parse_http_response "$response" "HTTP_CODE")
    local response_body=$(parse_http_response "$response" "RESPONSE")
    local error_msg=$(parse_http_response "$response" "ERROR")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ "$status_code" == "200" ]]; then
        # Validate response format
        local validation_result=$(validate_health_response "$response_body" "$service_name")
        
        if [[ "$validation_result" == SUCCESS:* ]]; then
            report_test_result \
                "$service_name Health Check" \
                "PASS" \
                "Service healthy (HTTP 200)" \
                "$duration" \
                "Response: $response_body"
            return 0
        else
            report_test_result \
                "$service_name Health Check" \
                "FAIL" \
                "Invalid health response format" \
                "$duration" \
                "Validation error: $validation_result | Response: $response_body"
            return 1
        fi
    else
        local failure_reason="HTTP $status_code"
        if [[ -n "$error_msg" ]]; then
            failure_reason="$failure_reason - $error_msg"
        elif [[ -n "$response_body" ]]; then
            failure_reason="$failure_reason - $response_body"
        fi
        
        report_test_result \
            "$service_name Health Check" \
            "FAIL" \
            "Service unhealthy" \
            "$duration" \
            "$failure_reason"
        return 1
    fi
}

# Test service readiness endpoint (if available)
test_service_readiness() {
    local service_name="$1"
    local port="$2"
    
    local start_time=$(date +%s)
    
    echo "Testing $service_name readiness endpoint..."
    
    local response=$(http_get "http://localhost:${port}/health/ready" "" "$TIMEOUT")
    local status_code=$(parse_http_response "$response" "HTTP_CODE")
    local response_body=$(parse_http_response "$response" "RESPONSE")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ "$status_code" == "200" ]]; then
        report_test_result \
            "$service_name Readiness Check" \
            "PASS" \
            "Service ready (HTTP 200)" \
            "$duration" \
            "Response: $response_body"
        return 0
    elif [[ "$status_code" == "404" ]]; then
        # Not all services may implement /health/ready
        report_test_result \
            "$service_name Readiness Check" \
            "SKIP" \
            "Readiness endpoint not implemented" \
            "$duration" \
            "HTTP 404 - endpoint not available"
        return 0
    else
        report_test_result \
            "$service_name Readiness Check" \
            "FAIL" \
            "Service not ready (HTTP $status_code)" \
            "$duration" \
            "Response: $response_body"
        return 1
    fi
}

# Test all services health endpoints
test_all_services_health() {
    report_phase_start "Service Health Verification" "Testing /health endpoints for all services"
    
    local phase_start_time=$(date +%s)
    local failed_services=()
    
    for service_name in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service_name]}"
        
        echo
        echo "=== Testing $service_name on port $port ==="
        
        # Test health endpoint
        if ! test_service_health "$service_name" "$port"; then
            failed_services+=("$service_name")
        fi
        
        # Test readiness endpoint
        test_service_readiness "$service_name" "$port"
        
        # Brief pause between services
        sleep 1
    done
    
    local phase_end_time=$(date +%s)
    local phase_duration=$((phase_end_time - phase_start_time))
    
    # Report phase completion
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        report_phase_complete "Service Health Verification" "PASS" "$phase_duration"
        return 0
    else
        echo
        echo "Failed services: ${failed_services[*]}"
        report_phase_complete "Service Health Verification" "FAIL" "$phase_duration"
        return 1
    fi
}

# Test service response times
test_response_times() {
    report_phase_start "Response Time Testing" "Measuring service response times"
    
    local phase_start_time=$(date +%s)
    
    for service_name in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service_name]}"
        
        echo "Measuring response time for $service_name..."
        
        local start_time=$(date +%s%3N)  # milliseconds
        local response=$(http_get "http://localhost:${port}${HEALTH_ENDPOINT}" "" "$TIMEOUT")
        local end_time=$(date +%s%3N)
        
        local response_time=$((end_time - start_time))
        local status_code=$(parse_http_response "$response" "HTTP_CODE")
        
        if [[ "$status_code" == "200" ]]; then
            if [[ $response_time -lt 1000 ]]; then  # Less than 1 second
                report_test_result \
                    "$service_name Response Time" \
                    "PASS" \
                    "Fast response (${response_time}ms)" \
                    "0" \
                    "Response time within acceptable range"
            elif [[ $response_time -lt 5000 ]]; then  # Less than 5 seconds
                report_test_result \
                    "$service_name Response Time" \
                    "PASS" \
                    "Acceptable response (${response_time}ms)" \
                    "0" \
                    "Response time acceptable but could be optimized"
            else
                report_test_result \
                    "$service_name Response Time" \
                    "FAIL" \
                    "Slow response (${response_time}ms)" \
                    "0" \
                    "Response time exceeds acceptable threshold"
            fi
        else
            report_test_result \
                "$service_name Response Time" \
                "FAIL" \
                "Service unreachable" \
                "0" \
                "HTTP $status_code - cannot measure response time"
        fi
    done
    
    local phase_end_time=$(date +%s)
    local phase_duration=$((phase_end_time - phase_start_time))
    
    report_phase_complete "Response Time Testing" "PASS" "$phase_duration"
}

# Main execution
main() {
    echo "Starting Health Check Tests for Project Zero App"
    echo "==============================================="
    
    local start_time=$(date +%s)
    
    # Run health check tests
    if ! test_all_services_health; then
        echo "Health check tests failed. Skipping response time tests."
        local end_time=$(date +%s)
        generate_summary "$start_time" "$end_time"
        return 1
    fi
    
    # Run response time tests
    test_response_times
    
    # Generate final report
    local end_time=$(date +%s)
    
    echo
    echo "Health Check Tests Completed"
    echo "============================"
    
    if generate_summary "$start_time" "$end_time"; then
        echo "All health check tests passed successfully!"
        return 0
    else
        echo "Some health check tests failed."
        return 1
    fi
}

# Execute main function
main "$@"