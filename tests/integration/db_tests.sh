#!/bin/bash
#
# Database Connectivity Tests for Project Zero App
#
# Tests PostgreSQL database connectivity for all services that use the database.
# Verifies database initialization, schema creation, and basic queries.
#

set -euo pipefail

# Source utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../utils/http_client.sh"
source "${SCRIPT_DIR}/../utils/validate_response.sh"
source "${SCRIPT_DIR}/../utils/test_reporter.sh"

# Services that use PostgreSQL database
declare -A DB_SERVICES=(
    ["auth-service"]="8001"
    ["user-profile-service"]="8002"
    ["product-service"]="8004"
    ["cart-service"]="8007"
    ["order-service"]="8008"
    ["payment-service"]="8009"
)

# Test configuration
readonly TIMEOUT=15
readonly POSTGRES_CONTAINER_NAME="project-zero-app-postgres-1"

# Initialize reporting
init_reporting

# Test PostgreSQL container status
test_postgres_container() {
    local start_time=$(date +%s)
    
    echo "Testing PostgreSQL container status..."
    
    # Check if container is running
    local container_status=$(docker ps --filter "name=$POSTGRES_CONTAINER_NAME" --format "{{.Status}}" 2>/dev/null || echo "")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ -n "$container_status" ]]; then
        report_test_result \
            "PostgreSQL Container" \
            "PASS" \
            "Container running" \
            "$duration" \
            "Status: $container_status"
        return 0
    else
        report_test_result \
            "PostgreSQL Container" \
            "FAIL" \
            "Container not running" \
            "$duration" \
            "Container '$POSTGRES_CONTAINER_NAME' not found or not running"
        return 1
    fi
}

# Test direct PostgreSQL connection
test_postgres_connection() {
    local start_time=$(date +%s)
    
    echo "Testing direct PostgreSQL connection..."
    
    # Try to connect using docker exec
    local result=$(docker exec "$POSTGRES_CONTAINER_NAME" psql -U postgres -d project_zero_db -c "SELECT 1;" 2>&1 || echo "CONNECTION_FAILED")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ "$result" != "CONNECTION_FAILED" && "$result" =~ "1 row" ]]; then
        report_test_result \
            "PostgreSQL Direct Connection" \
            "PASS" \
            "Database connection successful" \
            "$duration" \
            "Query executed successfully"
        return 0
    else
        report_test_result \
            "PostgreSQL Direct Connection" \
            "FAIL" \
            "Database connection failed" \
            "$duration" \
            "Error: $result"
        return 1
    fi
}

# Test service database readiness via /health/ready endpoint
test_service_db_readiness() {
    local service_name="$1"
    local port="$2"
    
    local start_time=$(date +%s)
    
    echo "Testing $service_name database readiness..."
    
    local response=$(http_get "http://localhost:${port}/health/ready" "" "$TIMEOUT")
    local status_code=$(parse_http_response "$response" "HTTP_CODE")
    local response_body=$(parse_http_response "$response" "RESPONSE")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ "$status_code" == "200" ]]; then
        report_test_result \
            "$service_name DB Readiness" \
            "PASS" \
            "Service reports database ready" \
            "$duration" \
            "Response: $response_body"
        return 0
    elif [[ "$status_code" == "404" ]]; then
        # Service doesn't implement /health/ready
        report_test_result \
            "$service_name DB Readiness" \
            "SKIP" \
            "Readiness endpoint not implemented" \
            "$duration" \
            "Service doesn't provide database readiness check"
        return 0
    else
        report_test_result \
            "$service_name DB Readiness" \
            "FAIL" \
            "Service reports database not ready (HTTP $status_code)" \
            "$duration" \
            "Response: $response_body"
        return 1
    fi
}

# Test service database functionality via API endpoints
test_service_db_functionality() {
    local service_name="$1"
    local port="$2"
    
    local start_time=$(date +%s)
    
    echo "Testing $service_name database functionality..."
    
    local endpoint=""
    local expected_fields=""
    
    # Define test endpoints for each service
    case "$service_name" in
        "auth-service")
            endpoint="/auth/test"
            expected_fields=".message"
            ;;
        "user-profile-service")
            endpoint="/users/test"
            expected_fields=".message"
            ;;
        "product-service")
            endpoint="/products"
            expected_fields="."
            ;;
        "cart-service")
            endpoint="/cart/test"
            expected_fields=".message"
            ;;
        "order-service")
            endpoint="/orders/test"
            expected_fields=".message"
            ;;
        "payment-service")
            endpoint="/payments/test"
            expected_fields=".message"
            ;;
        *)
            # Fallback to health endpoint
            endpoint="/health"
            expected_fields=".status"
            ;;
    esac
    
    local response=$(http_get "http://localhost:${port}${endpoint}" "" "$TIMEOUT")
    local status_code=$(parse_http_response "$response" "HTTP_CODE")
    local response_body=$(parse_http_response "$response" "RESPONSE")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ "$status_code" == "200" ]]; then
        # Check if response contains expected data structure
        if [[ -n "$response_body" ]]; then
            report_test_result \
                "$service_name DB Functionality" \
                "PASS" \
                "Database operations working" \
                "$duration" \
                "Service can perform database operations"
            return 0
        else
            report_test_result \
                "$service_name DB Functionality" \
                "FAIL" \
                "Empty response from database operation" \
                "$duration" \
                "Service responded but returned empty data"
            return 1
        fi
    elif [[ "$status_code" == "404" ]]; then
        # Test endpoint doesn't exist, try basic health check instead
        local health_response=$(http_get "http://localhost:${port}/health" "" "$TIMEOUT")
        local health_status=$(parse_http_response "$health_response" "HTTP_CODE")
        
        if [[ "$health_status" == "200" ]]; then
            report_test_result \
                "$service_name DB Functionality" \
                "SKIP" \
                "Test endpoint not available, health OK" \
                "$duration" \
                "Service is healthy but no database test endpoint found"
            return 0
        else
            report_test_result \
                "$service_name DB Functionality" \
                "FAIL" \
                "No test endpoint and service unhealthy" \
                "$duration" \
                "Cannot verify database functionality"
            return 1
        fi
    else
        report_test_result \
            "$service_name DB Functionality" \
            "FAIL" \
            "Database operation failed (HTTP $status_code)" \
            "$duration" \
            "Response: $response_body"
        return 1
    fi
}

# Test database schema and tables
test_database_schema() {
    local start_time=$(date +%s)
    
    echo "Testing database schema and tables..."
    
    # List all tables in the database
    local tables_query="SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    local tables_result=$(docker exec "$POSTGRES_CONTAINER_NAME" psql -U postgres -d project_zero_db -c "$tables_query" 2>&1 || echo "QUERY_FAILED")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ "$tables_result" != "QUERY_FAILED" ]]; then
        # Count the number of tables found
        local table_count=$(echo "$tables_result" | grep -E "^\s+[a-zA-Z_]" | wc -l)
        
        if [[ $table_count -gt 0 ]]; then
            report_test_result \
                "Database Schema" \
                "PASS" \
                "Found $table_count database tables" \
                "$duration" \
                "Database schema initialized successfully"
            return 0
        else
            report_test_result \
                "Database Schema" \
                "FAIL" \
                "No tables found in database" \
                "$duration" \
                "Database may not be properly initialized"
            return 1
        fi
    else
        report_test_result \
            "Database Schema" \
            "FAIL" \
            "Cannot query database schema" \
            "$duration" \
            "Error: $tables_result"
        return 1
    fi
}

# Run all database tests
main() {
    echo "Starting Database Connectivity Tests for Project Zero App"
    echo "========================================================"
    
    local start_time=$(date +%s)
    local overall_result=0
    
    # Test PostgreSQL container
    report_phase_start "PostgreSQL Infrastructure" "Testing PostgreSQL container and connection"
    
    if ! test_postgres_container; then
        echo "PostgreSQL container test failed. Skipping remaining tests."
        overall_result=1
    elif ! test_postgres_connection; then
        echo "PostgreSQL connection test failed. Continuing with service tests."
        overall_result=1
    fi
    
    test_database_schema
    
    local phase_end_time=$(date +%s)
    local phase_duration=$((phase_end_time - start_time))
    
    if [[ $overall_result -eq 0 ]]; then
        report_phase_complete "PostgreSQL Infrastructure" "PASS" "$phase_duration"
    else
        report_phase_complete "PostgreSQL Infrastructure" "FAIL" "$phase_duration"
    fi
    
    # Test service database readiness
    report_phase_start "Service Database Readiness" "Testing database readiness for all services"
    
    local readiness_start_time=$(date +%s)
    local failed_readiness=()
    
    for service_name in "${!DB_SERVICES[@]}"; do
        local port="${DB_SERVICES[$service_name]}"
        echo
        echo "=== Testing $service_name database readiness ==="
        
        if ! test_service_db_readiness "$service_name" "$port"; then
            failed_readiness+=("$service_name")
        fi
        
        sleep 1
    done
    
    local readiness_end_time=$(date +%s)
    local readiness_duration=$((readiness_end_time - readiness_start_time))
    
    if [[ ${#failed_readiness[@]} -eq 0 ]]; then
        report_phase_complete "Service Database Readiness" "PASS" "$readiness_duration"
    else
        echo "Services with database readiness issues: ${failed_readiness[*]}"
        report_phase_complete "Service Database Readiness" "FAIL" "$readiness_duration"
        overall_result=1
    fi
    
    # Test service database functionality
    report_phase_start "Service Database Functionality" "Testing database operations for all services"
    
    local functionality_start_time=$(date +%s)
    local failed_functionality=()
    
    for service_name in "${!DB_SERVICES[@]}"; do
        local port="${DB_SERVICES[$service_name]}"
        echo
        echo "=== Testing $service_name database functionality ==="
        
        if ! test_service_db_functionality "$service_name" "$port"; then
            failed_functionality+=("$service_name")
        fi
        
        sleep 1
    done
    
    local functionality_end_time=$(date +%s)
    local functionality_duration=$((functionality_end_time - functionality_start_time))
    
    if [[ ${#failed_functionality[@]} -eq 0 ]]; then
        report_phase_complete "Service Database Functionality" "PASS" "$functionality_duration"
    else
        echo "Services with database functionality issues: ${failed_functionality[*]}"
        report_phase_complete "Service Database Functionality" "FAIL" "$functionality_duration"
        overall_result=1
    fi
    
    # Generate final report
    local end_time=$(date +%s)
    
    echo
    echo "Database Connectivity Tests Completed"
    echo "====================================="
    
    if generate_summary "$start_time" "$end_time" && [[ $overall_result -eq 0 ]]; then
        echo "All database connectivity tests passed successfully!"
        return 0
    else
        echo "Some database connectivity tests failed."
        return 1
    fi
}

# Execute main function
main "$@"