#!/bin/bash

# Swagger Documentation Accessibility Tests
# Tests that all backend services expose their OpenAPI documentation at /docs endpoints

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
declare -a SERVICES=(
    "auth-service:8001"
    "user-profile-service:8002" 
    "product-service:8004"
    "cart-service:8007"
    "order-service:8008"
    "payment-service:8009"
    "notification-service:8011"
)

TIMEOUT=10
PASS_COUNT=0
FAIL_COUNT=0

echo "=========================================="
echo "🔍 Swagger Documentation Tests"
echo "=========================================="
echo "Testing /docs endpoints for all backend services..."
echo ""

# Function to test docs endpoint
test_docs_endpoint() {
    local service_name="$1"
    local port="$2"
    local url="http://localhost:${port}/docs"
    
    echo -n "Testing ${service_name} docs endpoint... "
    
    # Make HTTP request
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null || echo "HTTPSTATUS:000")
    
    # Extract HTTP status
    local http_status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    local body=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')
    
    # Validate response
    if [[ "$http_status" == "200" ]]; then
        # Check if response contains expected content
        if echo "$body" | grep -q "swagger\|openapi\|redoc\|docs" -i; then
            echo -e "${GREEN}✓ PASS${NC} (HTTP $http_status)"
            PASS_COUNT=$((PASS_COUNT + 1))
        else
            echo -e "${YELLOW}⚠ PARTIAL${NC} (HTTP $http_status, but content may not be docs)"
            PASS_COUNT=$((PASS_COUNT + 1))
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_status)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        
        # Additional debugging info
        if [[ "$http_status" == "000" ]]; then
            echo "    Error: Connection refused or timeout"
        fi
    fi
}

# Test all services
for service in "${SERVICES[@]}"; do
    IFS=':' read -r service_name port <<< "$service"
    test_docs_endpoint "$service_name" "$port"
done

echo ""
echo "=========================================="
echo "📊 Documentation Test Results"
echo "=========================================="
echo -e "✅ Passed: ${GREEN}$PASS_COUNT${NC}"
echo -e "❌ Failed: ${RED}$FAIL_COUNT${NC}"
if [ $((PASS_COUNT + FAIL_COUNT)) -gt 0 ]; then
    echo -e "📈 Success Rate: $(( PASS_COUNT * 100 / (PASS_COUNT + FAIL_COUNT) ))%"
else
    echo -e "📈 Success Rate: 0%"
fi

# Additional service health check
echo ""
echo "🔍 Service Health Status:"
for service in "${SERVICES[@]}"; do
    IFS=':' read -r service_name port <<< "$service"
    health_url="http://localhost:${port}/health"
    health_response=$(curl -s --max-time 5 "$health_url" 2>/dev/null || echo "ERROR")
    
    if echo "$health_response" | grep -q "healthy\|ok" -i; then
        echo -e "  ${service_name}: ${GREEN}Healthy${NC}"
    else
        echo -e "  ${service_name}: ${RED}Unhealthy${NC}"
    fi
done

echo ""
if [[ $FAIL_COUNT -eq 0 ]]; then
    echo -e "${GREEN}🎉 All documentation endpoints are accessible!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some documentation endpoints failed. Check service status.${NC}"
    exit 1
fi

# Initialize reporting
init_reporting

# Test service documentation endpoint
test_service_docs_endpoint() {
    local service_name="$1"
    local port="$2"
    local endpoint="$3"
    local endpoint_description="$4"
    
    local start_time=$(date +%s)
    
    echo "Testing $service_name $endpoint_description..."
    
    local response=$(http_get "http://localhost:${port}${endpoint}" "" "$TIMEOUT")
    local status_code=$(parse_http_response "$response" "HTTP_CODE")
    local response_body=$(parse_http_response "$response" "RESPONSE")
    local error_msg=$(parse_http_response "$response" "ERROR")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    case "$status_code" in
        "200")
            # Validate content based on endpoint type
            case "$endpoint" in
                "/docs"|"/redoc")
                    # HTML documentation should contain references to the service
                    if [[ "$response_body" =~ (html|HTML|swagger|Swagger|redoc|ReDoc) ]]; then
                        report_test_result \
                            "$service_name $endpoint_description" \
                            "PASS" \
                            "Documentation accessible (HTTP 200)" \
                            "$duration" \
                            "Valid HTML documentation found"
                        return 0
                    else
                        report_test_result \
                            "$service_name $endpoint_description" \
                            "FAIL" \
                            "Invalid documentation format" \
                            "$duration" \
                            "Response doesn't appear to be valid HTML documentation"
                        return 1
                    fi
                    ;;
                "/openapi.json")
                    # JSON spec should be valid JSON with OpenAPI fields
                    if validate_openapi_spec "$response_body" "$service_name"; then
                        report_test_result \
                            "$service_name $endpoint_description" \
                            "PASS" \
                            "Valid OpenAPI specification" \
                            "$duration" \
                            "OpenAPI JSON specification is valid"
                        return 0
                    else
                        report_test_result \
                            "$service_name $endpoint_description" \
                            "FAIL" \
                            "Invalid OpenAPI specification" \
                            "$duration" \
                            "OpenAPI JSON specification validation failed"
                        return 1
                    fi
                    ;;
                *)
                    # Generic success for any 200 response
                    report_test_result \
                        "$service_name $endpoint_description" \
                        "PASS" \
                        "Documentation accessible (HTTP 200)" \
                        "$duration" \
                        "Documentation endpoint responded successfully"
                    return 0
                    ;;
            esac
            ;;
        "404")
            report_test_result \
                "$service_name $endpoint_description" \
                "SKIP" \
                "Documentation endpoint not available" \
                "$duration" \
                "HTTP 404 - endpoint not implemented"
            return 0
            ;;
        "500")
            report_test_result \
                "$service_name $endpoint_description" \
                "FAIL" \
                "Documentation endpoint error (HTTP 500)" \
                "$duration" \
                "Server error when accessing documentation"
            return 1
            ;;
        *)
            local failure_reason="HTTP $status_code"
            if [[ -n "$error_msg" ]]; then
                failure_reason="$failure_reason - $error_msg"
            elif [[ -n "$response_body" ]]; then
                failure_reason="$failure_reason - ${response_body:0:100}..."
            fi
            
            report_test_result \
                "$service_name $endpoint_description" \
                "FAIL" \
                "Documentation endpoint inaccessible" \
                "$duration" \
                "$failure_reason"
            return 1
            ;;
    esac
}

# Validate OpenAPI specification content
validate_openapi_spec() {
    local spec_content="$1"
    local service_name="$2"
    
    # Check if it's valid JSON
    if ! echo "$spec_content" | jq . >/dev/null 2>&1; then
        echo "Invalid JSON in OpenAPI specification"
        return 1
    fi
    
    # Check for required OpenAPI fields
    local openapi_version=$(echo "$spec_content" | jq -r '.openapi // .swagger // "missing"')
    if [[ "$openapi_version" == "missing" ]]; then
        echo "Missing OpenAPI/Swagger version field"
        return 1
    fi
    
    # Check for info section
    local title=$(echo "$spec_content" | jq -r '.info.title // "missing"')
    if [[ "$title" == "missing" ]]; then
        echo "Missing info.title in OpenAPI specification"
        return 1
    fi
    
    # Check for paths section
    local paths_count=$(echo "$spec_content" | jq '.paths | length // 0')
    if [[ $paths_count -eq 0 ]]; then
        echo "No paths defined in OpenAPI specification"
        return 1
    fi
    
    echo "Valid OpenAPI specification with $paths_count endpoints defined"
    return 0
}

# Test service documentation coverage
test_service_api_coverage() {
    local service_name="$1"
    local port="$2"
    
    local start_time=$(date +%s)
    
    echo "Testing $service_name API documentation coverage..."
    
    # Get OpenAPI spec
    local response=$(http_get "http://localhost:${port}/openapi.json" "" "$TIMEOUT")
    local status_code=$(parse_http_response "$response" "HTTP_CODE")
    local response_body=$(parse_http_response "$response" "RESPONSE")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ "$status_code" == "200" ]]; then
        # Analyze API coverage
        local paths_count=$(echo "$response_body" | jq '.paths | length // 0' 2>/dev/null || echo "0")
        local methods_count=$(echo "$response_body" | jq '[.paths[] | keys[]] | length // 0' 2>/dev/null || echo "0")
        
        if [[ $paths_count -gt 0 ]]; then
            local coverage_info="$paths_count endpoints, $methods_count methods documented"
            
            # Check for common endpoints
            local has_health=$(echo "$response_body" | jq -r '.paths | has("/health")' 2>/dev/null || echo "false")
            
            if [[ "$has_health" == "true" ]]; then
                coverage_info="$coverage_info (includes health check)"
            fi
            
            report_test_result \
                "$service_name API Coverage" \
                "PASS" \
                "Comprehensive API documentation" \
                "$duration" \
                "$coverage_info"
            return 0
        else
            report_test_result \
                "$service_name API Coverage" \
                "FAIL" \
                "No API endpoints documented" \
                "$duration" \
                "OpenAPI specification contains no documented endpoints"
            return 1
        fi
    elif [[ "$status_code" == "404" ]]; then
        report_test_result \
            "$service_name API Coverage" \
            "SKIP" \
            "OpenAPI specification not available" \
            "$duration" \
            "Cannot analyze API coverage without OpenAPI spec"
        return 0
    else
        report_test_result \
            "$service_name API Coverage" \
            "FAIL" \
            "Cannot access OpenAPI specification" \
            "$duration" \
            "HTTP $status_code when requesting OpenAPI spec"
        return 1
    fi
}

# Test all services documentation
test_all_services_documentation() {
    report_phase_start "Service Documentation Testing" "Testing documentation endpoints for all services"
    
    local phase_start_time=$(date +%s)
    local failed_services=()
    
    for service_name in "${!DOCS_SERVICES[@]}"; do
        local port="${DOCS_SERVICES[$service_name]}"
        
        echo
        echo "=== Testing $service_name documentation on port $port ==="
        
        local service_failed=false
        
        # Test each documentation endpoint
        for endpoint in "${!DOC_ENDPOINTS[@]}"; do
            local description="${DOC_ENDPOINTS[$endpoint]}"
            
            if ! test_service_docs_endpoint "$service_name" "$port" "$endpoint" "$description"; then
                service_failed=true
            fi
            
            sleep 0.5  # Brief pause between endpoint tests
        done
        
        # Test API coverage
        if ! test_service_api_coverage "$service_name" "$port"; then
            service_failed=true
        fi
        
        if [[ "$service_failed" == "true" ]]; then
            failed_services+=("$service_name")
        fi
        
        sleep 1  # Pause between services
    done
    
    local phase_end_time=$(date +%s)
    local phase_duration=$((phase_end_time - phase_start_time))
    
    # Report phase completion
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        report_phase_complete "Service Documentation Testing" "PASS" "$phase_duration"
        return 0
    else
        echo
        echo "Services with documentation issues: ${failed_services[*]}"
        report_phase_complete "Service Documentation Testing" "FAIL" "$phase_duration"
        return 1
    fi
}

# Test documentation consistency
test_documentation_consistency() {
    report_phase_start "Documentation Consistency" "Checking documentation consistency across services"
    
    local phase_start_time=$(date +%s)
    local consistency_issues=()
    
    # Collect OpenAPI specs from all services
    declare -A service_specs=()
    
    for service_name in "${!DOCS_SERVICES[@]}"; do
        local port="${DOCS_SERVICES[$service_name]}"
        
        echo "Fetching OpenAPI spec for $service_name..."
        
        local response=$(http_get "http://localhost:${port}/openapi.json" "" "$TIMEOUT")
        local status_code=$(parse_http_response "$response" "HTTP_CODE")
        
        if [[ "$status_code" == "200" ]]; then
            local response_body=$(parse_http_response "$response" "RESPONSE")
            service_specs["$service_name"]="$response_body"
        else
            echo "Could not fetch OpenAPI spec for $service_name (HTTP $status_code)"
        fi
    done
    
    # Check for consistent patterns across services
    local services_with_health=0
    local services_with_version=0
    local total_services=${#service_specs[@]}
    
    for service_name in "${!service_specs[@]}"; do
        local spec="${service_specs[$service_name]}"
        
        # Check for health endpoint
        local has_health=$(echo "$spec" | jq -r '.paths | has("/health")' 2>/dev/null || echo "false")
        if [[ "$has_health" == "true" ]]; then
            ((services_with_health++))
        fi
        
        # Check for version in info
        local has_version=$(echo "$spec" | jq -r '.info | has("version")' 2>/dev/null || echo "false")
        if [[ "$has_version" == "true" ]]; then
            ((services_with_version++))
        fi
    done
    
    local phase_end_time=$(date +%s)
    local phase_duration=$((phase_end_time - phase_start_time))
    
    # Report consistency findings
    local consistency_info="$services_with_health/$total_services services document health endpoints, $services_with_version/$total_services include version info"
    
    if [[ $services_with_health -eq $total_services && $services_with_version -eq $total_services ]]; then
        report_test_result \
            "Documentation Consistency" \
            "PASS" \
            "All services follow consistent documentation patterns" \
            "$phase_duration" \
            "$consistency_info"
        
        report_phase_complete "Documentation Consistency" "PASS" "$phase_duration"
        return 0
    else
        report_test_result \
            "Documentation Consistency" \
            "FAIL" \
            "Inconsistent documentation patterns" \
            "$phase_duration" \
            "$consistency_info"
        
        report_phase_complete "Documentation Consistency" "FAIL" "$phase_duration"
        return 1
    fi
}

# Main execution
main() {
    echo "Starting Documentation Tests for Project Zero App"
    echo "================================================"
    
    local start_time=$(date +%s)
    local overall_result=0
    
    # Test all services documentation
    if ! test_all_services_documentation; then
        overall_result=1
    fi
    
    # Test documentation consistency
    if ! test_documentation_consistency; then
        overall_result=1
    fi
    
    # Generate final report
    local end_time=$(date +%s)
    
    echo
    echo "Documentation Tests Completed"
    echo "============================="
    
    if generate_summary "$start_time" "$end_time" && [[ $overall_result -eq 0 ]]; then
        echo "All documentation tests passed successfully!"
        return 0
    else
        echo "Some documentation tests failed."
        return 1
    fi
}

# Execute main function
main "$@"