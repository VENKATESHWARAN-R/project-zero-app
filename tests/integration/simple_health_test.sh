#!/bin/bash
#
# Simple Health Check Test
# Tests all services for basic health endpoint response
#

set -e

echo "🏥 Testing Health Endpoints for Project Zero App Services"
echo "========================================================="

# Array of services and ports
services=(
    "auth-service:8001"
    "user-profile-service:8002"  
    "product-service:8004"
    "cart-service:8007"
    "order-service:8008"
    "payment-service:8009"
    "notification-service:8011"
    "api-gateway:8000"
    "frontend:3000"
)

total_tests=0
passed_tests=0
failed_tests=0

for service_port in "${services[@]}"; do
    service=$(echo "$service_port" | cut -d: -f1)
    port=$(echo "$service_port" | cut -d: -f2)
    total_tests=$((total_tests + 1))
    
    echo -n "Testing $service (port $port)... "
    
    if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ PASS"
        passed_tests=$((passed_tests + 1))
    else
        echo "❌ FAIL"
        failed_tests=$((failed_tests + 1))
        # Try to get more details
        echo "   Details: $(curl -s "http://localhost:$port/health" 2>&1 || echo "Service not responding")"
    fi
done

echo ""
echo "========================================================="
echo "📊 Test Results Summary:"
echo "   Total Tests: $total_tests"
echo "   Passed: $passed_tests"
echo "   Failed: $failed_tests"
echo "   Success Rate: $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc -l 2>/dev/null || echo "N/A")%"

if [ $failed_tests -eq 0 ]; then
    echo "🎉 All health checks passed!"
    exit 0
else
    echo "⚠️  Some health checks failed. Please review the details above."
    exit 1
fi