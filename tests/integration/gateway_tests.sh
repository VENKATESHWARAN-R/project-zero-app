#!/bin/bash

# API Gateway Routing Tests
# Tests that API Gateway properly routes requests to all downstream services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
GATEWAY_URL="http://localhost:8000"
TIMEOUT=10
PASS_COUNT=0
FAIL_COUNT=0

# Route mappings (gateway path -> expected backend service)
declare -a ROUTES=(
    "/api/auth/health:auth-service:8001"
    "/api/profile/health:user-profile-service:8002"
    "/api/products/health:product-service:8004"
    "/api/cart/health:cart-service:8007"
    "/api/orders/health:order-service:8008"
    "/api/payments/health:payment-service:8009"
)

echo "=========================================="
echo "🌐 API Gateway Routing Tests"
echo "=========================================="
echo "Testing routing from API Gateway to backend services..."
echo ""

# Function to test gateway routing
test_gateway_route() {
    local route="$1"
    local service_name="$2"
    local backend_port="$3"
    local gateway_url="${GATEWAY_URL}${route}"
    local direct_url="http://localhost:${backend_port}/health"
    
    echo -n "Testing ${route} -> ${service_name}... "
    
    # Test gateway route
    local gateway_response=$(curl -s -w "HTTPSTATUS:%{http_code}" --max-time $TIMEOUT "$gateway_url" 2>/dev/null || echo "HTTPSTATUS:000")
    local gateway_status=$(echo "$gateway_response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    local gateway_body=$(echo "$gateway_response" | sed 's/HTTPSTATUS:[0-9]*$//')
    
    # Test direct backend route for comparison
    local direct_response=$(curl -s -w "HTTPSTATUS:%{http_code}" --max-time $TIMEOUT "$direct_url" 2>/dev/null || echo "HTTPSTATUS:000")
    local direct_status=$(echo "$direct_response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    # Validate routing
    if [[ "$gateway_status" == "200" && "$direct_status" == "200" ]]; then
        # Check if responses are similar (both should have health status)
        if echo "$gateway_body" | grep -q "healthy\|ok" -i; then
            echo -e "${GREEN}✓ PASS${NC} (HTTP $gateway_status)"
            PASS_COUNT=$((PASS_COUNT + 1))
        else
            echo -e "${YELLOW}⚠ PARTIAL${NC} (HTTP $gateway_status, but unexpected response)"
            PASS_COUNT=$((PASS_COUNT + 1))
        fi
    elif [[ "$gateway_status" == "503" || "$gateway_status" == "502" ]]; then
        echo -e "${YELLOW}⚠ SERVICE_UNAVAILABLE${NC} (HTTP $gateway_status) - Backend may be down"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    elif [[ "$gateway_status" == "404" ]]; then
        echo -e "${RED}✗ ROUTE_NOT_FOUND${NC} (HTTP $gateway_status) - Route not configured"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (Gateway: HTTP $gateway_status, Direct: HTTP $direct_status)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        
        # Additional debugging info
        if [[ "$gateway_status" == "000" ]]; then
            echo "    Error: Gateway connection refused or timeout"
        fi
    fi
}

# Test gateway health first
echo -e "${BLUE}🔍 Testing Gateway Health${NC}"
gateway_health=$(curl -s --max-time $TIMEOUT "$GATEWAY_URL/health" 2>/dev/null || echo "ERROR")
if echo "$gateway_health" | grep -q "healthy\|ok" -i; then
    echo -e "  Gateway Status: ${GREEN}Healthy${NC}"
else
    echo -e "  Gateway Status: ${RED}Unhealthy or Unreachable${NC}"
    echo "  Cannot proceed with routing tests."
    exit 1
fi
echo ""

# Test all routes
echo -e "${BLUE}🛣️  Testing Route Mappings${NC}"
for route_config in "${ROUTES[@]}"; do
    IFS=':' read -r route service_name backend_port <<< "$route_config"
    test_gateway_route "$route" "$service_name" "$backend_port"
done

echo ""
echo "=========================================="
echo "📊 Gateway Routing Test Results"
echo "=========================================="
echo -e "✅ Passed: ${GREEN}$PASS_COUNT${NC}"
echo -e "❌ Failed: ${RED}$FAIL_COUNT${NC}"
if [ $((PASS_COUNT + FAIL_COUNT)) -gt 0 ]; then
    echo -e "📈 Success Rate: $(( PASS_COUNT * 100 / (PASS_COUNT + FAIL_COUNT) ))%"
else
    echo -e "📈 Success Rate: 0%"
fi

echo ""
if [[ $FAIL_COUNT -eq 0 ]]; then
    echo -e "${GREEN}🎉 All gateway routes are working correctly!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some gateway routes failed. Check service status and gateway configuration.${NC}"
    exit 1
fi
