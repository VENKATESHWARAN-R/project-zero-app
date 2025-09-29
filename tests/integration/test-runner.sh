#!/bin/bash
#
# Integration Test Runner for Project Zero App
# 
# This script orchestrates the complete integration test suite, including:
# - Service health verification
# - Database connectivity testing  
# - Authentication flow testing
# - End-to-end workflow testing
# - Error reporting and cleanup
#
# Usage: ./tests/integration/test-runner.sh [options]
#
# Options:
#   --skip-build     Skip Docker build step
#   --parallel       Run parallel-safe tests simultaneously  
#   --verbose        Enable verbose output
#   --cleanup        Clean up containers after tests
#   --help           Show this help message
#

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly TEST_UTILS_DIR="${PROJECT_ROOT}/tests/utils"
readonly TEST_RESULTS_DIR="${PROJECT_ROOT}/tests/results"
readonly TEST_LOGS_DIR="${PROJECT_ROOT}/tests/logs"

# Test configuration
readonly HEALTH_CHECK_TIMEOUT=30
readonly SERVICE_START_TIMEOUT=60
readonly API_REQUEST_TIMEOUT=10

# Service configuration
declare -a SERVICES=(
    "auth-service:8001"
    "user-profile-service:8002" 
    "product-service:8004"
    "cart-service:8007"
    "order-service:8008"
    "payment-service:8009"
    "notification-service:8011"
    "api-gateway:8000"
)

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Global variables
SKIP_BUILD=false
PARALLEL_MODE=false
VERBOSE=false
CLEANUP_AFTER=false
START_TIME=""
TEST_COUNT=0
PASSED_COUNT=0
FAILED_COUNT=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" | tee -a "${TEST_LOGS_DIR}/test-runner.log"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $*" | tee -a "${TEST_LOGS_DIR}/test-runner.log"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $*" | tee -a "${TEST_LOGS_DIR}/test-runner.log"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $*" | tee -a "${TEST_LOGS_DIR}/test-runner.log"
}

# Initialize test environment
init_test_environment() {
    log_info "Initializing test environment..."
    
    # Create result directories
    mkdir -p "${TEST_RESULTS_DIR}" "${TEST_LOGS_DIR}"
    
    # Clear previous logs
    > "${TEST_LOGS_DIR}/test-runner.log"
    
    # Record start time
    START_TIME=$(date +%s)
    
    # Source utility functions
    if [[ -f "${TEST_UTILS_DIR}/http_client.sh" ]]; then
        source "${TEST_UTILS_DIR}/http_client.sh"
    fi
    
    if [[ -f "${TEST_UTILS_DIR}/validate_response.sh" ]]; then
        source "${TEST_UTILS_DIR}/validate_response.sh"
    fi
    
    log_info "Test environment initialized"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --parallel)
                PARALLEL_MODE=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --cleanup)
                CLEANUP_AFTER=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Show help message
show_help() {
    cat << EOF
Integration Test Runner for Project Zero App

Usage: $0 [options]

Options:
    --skip-build     Skip Docker build step
    --parallel       Run parallel-safe tests simultaneously
    --verbose        Enable verbose output
    --cleanup        Clean up containers after tests
    --help           Show this help message

Examples:
    $0                           # Run full test suite
    $0 --skip-build --parallel   # Quick test run with parallel execution
    $0 --verbose --cleanup       # Verbose run with cleanup
EOF
}

# Start services with Docker Compose
start_services() {
    if [[ "${SKIP_BUILD}" == false ]]; then
        log_info "Building and starting services with Docker Compose..."
        cd "${PROJECT_ROOT}"
        docker-compose up -d --build
    else
        log_info "Starting services with Docker Compose (skip build)..."
        cd "${PROJECT_ROOT}"
        docker-compose up -d
    fi
    
    log_info "Waiting for services to start..."
    sleep "${SERVICE_START_TIMEOUT}"
}

# Wait for service health checks
wait_for_services() {
    log_info "Checking service health..."
    
    local all_healthy=true
    for service_info in "${SERVICES[@]}"; do
        local service_name="${service_info%:*}"
        local service_port="${service_info#*:}"
        
        log_info "Checking ${service_name} on port ${service_port}..."
        
        local attempts=0
        local max_attempts=10
        local healthy=false
        
        while [[ $attempts -lt $max_attempts ]]; do
            if curl -sf "http://localhost:${service_port}/health" > /dev/null 2>&1; then
                log_success "${service_name} is healthy"
                healthy=true
                break
            fi
            
            ((attempts++))
            log_warning "${service_name} not ready (attempt ${attempts}/${max_attempts})"
            sleep 3
        done
        
        if [[ "${healthy}" == false ]]; then
            log_error "${service_name} failed to start properly"
            all_healthy=false
        fi
    done
    
    if [[ "${all_healthy}" == false ]]; then
        log_error "Some services failed to start. Aborting tests."
        exit 1
    fi
    
    log_success "All services are healthy"
}

# Run test phase
run_test_phase() {
    local phase_name="$1"
    local test_script="$2"
    
    log_info "Running ${phase_name}..."
    
    if [[ -f "${test_script}" ]]; then
        if bash "${test_script}"; then
            log_success "${phase_name} completed"
            return 0
        else
            log_error "${phase_name} failed"
            return 1
        fi
    else
        log_warning "${phase_name} script not found: ${test_script}"
        return 1
    fi
}

# Main test execution
run_tests() {
    log_info "Starting Project Zero App Integration Tests"
    
    local test_phases=(
        "Health Check Tests:${SCRIPT_DIR}/health_tests.sh"
        "Database Connectivity Tests:${SCRIPT_DIR}/db_tests.sh"
        "API Gateway Tests:${SCRIPT_DIR}/gateway_tests.sh"
        "Authentication Flow Tests:${SCRIPT_DIR}/auth_tests.sh"
        "Product Service Tests:${SCRIPT_DIR}/product_tests.sh"
        "Cart Operations Tests:${SCRIPT_DIR}/cart_tests.sh"
        "User Profile Tests:${SCRIPT_DIR}/profile_tests.sh"
        "Order Flow Tests:${SCRIPT_DIR}/order_flow_tests.sh"
        "Service Communication Tests:${SCRIPT_DIR}/service_communication_tests.sh"
    )
    
    for phase_info in "${test_phases[@]}"; do
        local phase_name="${phase_info%:*}"
        local test_script="${phase_info#*:}"
        
        ((TEST_COUNT++))
        
        if run_test_phase "${phase_name}" "${test_script}"; then
            ((PASSED_COUNT++))
        else
            ((FAILED_COUNT++))
        fi
    done
}

# Generate test report
generate_report() {
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    local report_file="${TEST_RESULTS_DIR}/integration-$(date +%Y%m%d-%H%M%S).json"
    
    cat > "${report_file}" << EOF
{
  "timestamp": "${timestamp}",
  "duration_seconds": ${duration},
  "total_tests": ${TEST_COUNT},
  "passed_tests": ${PASSED_COUNT},
  "failed_tests": ${FAILED_COUNT},
  "success_rate": $(echo "scale=2; ${PASSED_COUNT} * 100 / ${TEST_COUNT}" | bc -l)%,
  "status": "$([ ${FAILED_COUNT} -eq 0 ] && echo "PASSED" || echo "FAILED")"
}
EOF
    
    log_info "Test report generated: ${report_file}"
    
    # Display summary
    echo
    echo "=========================================="
    echo "Integration Test Summary"
    echo "=========================================="
    echo "Duration: ${duration} seconds"
    echo "Total Tests: ${TEST_COUNT}"
    echo "Passed: ${PASSED_COUNT}"
    echo "Failed: ${FAILED_COUNT}"
    echo "Success Rate: $(echo "scale=1; ${PASSED_COUNT} * 100 / ${TEST_COUNT}" | bc -l)%"
    echo
    
    if [[ ${FAILED_COUNT} -eq 0 ]]; then
        log_success "🎉 All integration tests passed!"
        return 0
    else
        log_error "❌ ${FAILED_COUNT} test(s) failed"
        return 1
    fi
}

# Cleanup function
cleanup() {
    if [[ "${CLEANUP_AFTER}" == true ]]; then
        log_info "Cleaning up containers..."
        cd "${PROJECT_ROOT}"
        docker-compose down
    fi
}

# Trap cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    parse_arguments "$@"
    init_test_environment
    start_services
    wait_for_services
    run_tests
    generate_report
}

# Execute main function with all arguments
main "$@"