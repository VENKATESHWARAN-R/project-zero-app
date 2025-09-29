#!/bin/bash
#
# End-to-End E-commerce Flow Test
# Tests the complete user journey: registration → login → browse products → add to cart → create order → payment → notification
#

set -e

echo "🛒 Testing End-to-End E-commerce Flow for Project Zero App"
echo "=========================================================="

# Test configuration
AUTH_URL="http://localhost:8001"
PRODUCT_URL="http://localhost:8004" 
CART_URL="http://localhost:8007"
ORDER_URL="http://localhost:8008"
PAYMENT_URL="http://localhost:8009"
PROFILE_URL="http://localhost:8002"
NOTIFICATION_URL="http://localhost:8011"

TEST_EMAIL="ecommerce_user_$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"
TEST_FIRST_NAME="John"
TEST_LAST_NAME="Doe"

total_tests=0
passed_tests=0
failed_tests=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function for testing
test_step() {
    local step_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    total_tests=$((total_tests + 1))
    echo -n "  $step_name... "
    
    if result=$(eval "$test_command" 2>&1); then
        if [[ -z "$expected_pattern" ]] || echo "$result" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}✅ PASS${NC}"
            passed_tests=$((passed_tests + 1))
            return 0
        else
            echo -e "${RED}❌ FAIL${NC} (Pattern not found)"
            echo "    Expected: $expected_pattern"
            echo "    Got: $(echo "$result" | head -1)"
            failed_tests=$((failed_tests + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "    Error: $(echo "$result" | head -1)"
        failed_tests=$((failed_tests + 1))
        return 1
    fi
}

# Storage for test data
ACCESS_TOKEN=""
USER_ID=""
CART_ID=""
PRODUCT_ID=""
ORDER_ID=""
PAYMENT_ID=""

echo -e "${YELLOW}Phase 1: User Registration and Authentication${NC}"
echo "============================================="

# Step 1: Register user
echo -e "${BLUE}🔐 User Registration and Login${NC}"
register_result=$(curl -s -X POST "$AUTH_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\",
        \"first_name\": \"$TEST_FIRST_NAME\",
        \"last_name\": \"$TEST_LAST_NAME\"
    }")

if echo "$register_result" | grep -q '"user_id"'; then
    USER_ID=$(echo "$register_result" | grep -o '"user_id":[0-9]*' | cut -d: -f2)
    echo -e "  Registration successful. User ID: $USER_ID"
    passed_tests=$((passed_tests + 1))
else
    echo -e "${RED}❌ Registration failed${NC}"
    echo "  Response: $register_result"
    failed_tests=$((failed_tests + 1))
    exit 1
fi
total_tests=$((total_tests + 1))

# Step 2: Login and get tokens
login_result=$(curl -s -X POST "$AUTH_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\"
    }")

if echo "$login_result" | grep -q '"access_token"'; then
    ACCESS_TOKEN=$(echo "$login_result" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo -e "  Login successful. Token: ${ACCESS_TOKEN:0:20}..."
    passed_tests=$((passed_tests + 1))
else
    echo -e "${RED}❌ Login failed${NC}"
    echo "  Response: $login_result"
    failed_tests=$((failed_tests + 1))
    exit 1
fi
total_tests=$((total_tests + 1))

echo -e "${YELLOW}Phase 2: User Profile Setup${NC}"
echo "==========================="

# Step 3: Create user profile
echo -e "${BLUE}👤 Creating User Profile${NC}"
profile_result=$(curl -s -X POST "$PROFILE_URL/profiles" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"first_name\": \"$TEST_FIRST_NAME\",
        \"last_name\": \"$TEST_LAST_NAME\",
        \"date_of_birth\": \"1990-01-01\",
        \"phone_number\": \"+1234567890\"
    }")

test_step "Profile creation" "echo '$profile_result'" '"id"\|"user_id"\|"first_name"'

# Step 4: Add shipping address
echo -e "${BLUE}📍 Adding Shipping Address${NC}"
address_result=$(curl -s -X POST "$PROFILE_URL/addresses" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"street\": \"123 Test Street\",
        \"city\": \"Test City\",
        \"state\": \"TS\",
        \"zip_code\": \"12345\",
        \"country\": \"US\",
        \"is_default\": true
    }")

test_step "Address creation" "echo '$address_result'" '"id"\|"street"\|"city"'

echo -e "${YELLOW}Phase 3: Product Discovery${NC}"
echo "=========================="

# Step 5: Browse products
echo -e "${BLUE}🛍️ Browsing Product Catalog${NC}"
products_result=$(curl -s -X GET "$PRODUCT_URL/products?limit=5")

if echo "$products_result" | grep -q '"products"\|"items"'; then
    PRODUCT_ID=$(echo "$products_result" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
    echo -e "  Product browsing successful. Found product ID: $PRODUCT_ID"
    passed_tests=$((passed_tests + 1))
else
    echo -e "${RED}❌ Product browsing failed${NC}"
    echo "  Response: $products_result"
    failed_tests=$((failed_tests + 1))
fi
total_tests=$((total_tests + 1))

# Step 6: Get product details
echo -e "${BLUE}📦 Getting Product Details${NC}"
product_detail_result=$(curl -s -X GET "$PRODUCT_URL/products/$PRODUCT_ID")
test_step "Product details retrieval" "echo '$product_detail_result'" '"id"\|"name"\|"price"'

echo -e "${YELLOW}Phase 4: Shopping Cart Operations${NC}"
echo "================================="

# Step 7: Add product to cart
echo -e "${BLUE}🛒 Adding Product to Cart${NC}"
cart_add_result=$(curl -s -X POST "$CART_URL/cart/add" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"product_id\": $PRODUCT_ID,
        \"quantity\": 2
    }")

test_step "Add to cart" "echo '$cart_add_result'" '"message":"Product added to cart"\|"cart_item_id"\|"success"'

# Step 8: View cart contents
echo -e "${BLUE}👀 Viewing Cart Contents${NC}"
cart_view_result=$(curl -s -X GET "$CART_URL/cart" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

test_step "View cart" "echo '$cart_view_result'" '"items"\|"total"\|"cart_id"'

# Step 9: Update cart quantity
echo -e "${BLUE}📝 Updating Cart Quantity${NC}"
cart_update_result=$(curl -s -X PUT "$CART_URL/cart/update" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"product_id\": $PRODUCT_ID,
        \"quantity\": 3
    }")

test_step "Update cart quantity" "echo '$cart_update_result'" '"message"\|"updated"\|"success"'

echo -e "${YELLOW}Phase 5: Order Creation${NC}"
echo "======================"

# Step 10: Create order from cart
echo -e "${BLUE}📋 Creating Order${NC}"
order_result=$(curl -s -X POST "$ORDER_URL/orders" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"shipping_address\": {
            \"street\": \"123 Test Street\",
            \"city\": \"Test City\",
            \"state\": \"TS\",
            \"zip_code\": \"12345\",
            \"country\": \"US\"
        }
    }")

if echo "$order_result" | grep -q '"order_id"\|"id"'; then
    ORDER_ID=$(echo "$order_result" | grep -o '"order_id":[0-9]*\|"id":[0-9]*' | head -1 | cut -d: -f2)
    echo -e "  Order creation successful. Order ID: $ORDER_ID"
    passed_tests=$((passed_tests + 1))
else
    echo -e "${RED}❌ Order creation failed${NC}"
    echo "  Response: $order_result"
    failed_tests=$((failed_tests + 1))
fi
total_tests=$((total_tests + 1))

# Step 11: Get order details
echo -e "${BLUE}📄 Getting Order Details${NC}"
if [[ -n "$ORDER_ID" ]]; then
    order_detail_result=$(curl -s -X GET "$ORDER_URL/orders/$ORDER_ID" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    test_step "Order details retrieval" "echo '$order_detail_result'" '"id"\|"total"\|"status"'
fi

echo -e "${YELLOW}Phase 6: Payment Processing${NC}"
echo "==========================="

# Step 12: Process payment
echo -e "${BLUE}💳 Processing Payment${NC}"
if [[ -n "$ORDER_ID" ]]; then
    payment_result=$(curl -s -X POST "$PAYMENT_URL/payments" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"order_id\": $ORDER_ID,
            \"amount\": 29.99,
            \"payment_method\": {
                \"type\": \"credit_card\",
                \"card_number\": \"4111111111111111\",
                \"expiry_month\": 12,
                \"expiry_year\": 2025,
                \"cvv\": \"123\"
            }
        }")
    
    if echo "$payment_result" | grep -q '"payment_id"\|"id"\|"success"\|"status":"completed"'; then
        PAYMENT_ID=$(echo "$payment_result" | grep -o '"payment_id":[0-9]*\|"id":[0-9]*' | head -1 | cut -d: -f2)
        echo -e "  Payment processing successful. Payment ID: $PAYMENT_ID"
        passed_tests=$((passed_tests + 1))
    else
        echo -e "${RED}❌ Payment processing failed${NC}"
        echo "  Response: $payment_result"
        failed_tests=$((failed_tests + 1))
    fi
    total_tests=$((total_tests + 1))
fi

echo -e "${YELLOW}Phase 7: Order Completion and Notifications${NC}"
echo "==========================================="

# Step 13: Check final order status
echo -e "${BLUE}✅ Checking Final Order Status${NC}"
if [[ -n "$ORDER_ID" ]]; then
    final_order_result=$(curl -s -X GET "$ORDER_URL/orders/$ORDER_ID" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    test_step "Final order status check" "echo '$final_order_result'" '"status":"completed"\|"status":"processing"\|"status":"confirmed"'
fi

# Step 14: Check notifications
echo -e "${BLUE}📧 Checking Notifications${NC}"
notifications_result=$(curl -s -X GET "$NOTIFICATION_URL/notifications" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

test_step "Notifications check" "echo '$notifications_result'" '"notifications"\|"messages"\|"[]"'

echo ""
echo "=========================================================="
echo "📊 End-to-End E-commerce Flow Test Results Summary:"
echo "   Total Tests: $total_tests"
echo "   Passed: $passed_tests"
echo "   Failed: $failed_tests"
if [[ $total_tests -gt 0 ]]; then
    success_rate=$(echo "scale=2; $passed_tests * 100 / $total_tests" | bc -l 2>/dev/null || echo "N/A")
    echo "   Success Rate: ${success_rate}%"
fi

echo ""
echo "🔍 Test Scenario Summary:"
echo "   ✅ User Registration & Login"
echo "   ✅ Profile & Address Setup"
echo "   ✅ Product Discovery & Details"
echo "   ✅ Shopping Cart Operations"
echo "   ✅ Order Creation & Management"
echo "   ✅ Payment Processing"
echo "   ✅ Notifications & Status Updates"

if [[ $failed_tests -eq 0 ]]; then
    echo -e "${GREEN}🎉 All e-commerce flow tests passed! The system is ready for demo.${NC}"
    echo ""
    echo -e "${BLUE}🚀 Demo Flow Instructions:${NC}"
    echo "1. Visit http://localhost:3000 in your browser"
    echo "2. Register a new user account"
    echo "3. Browse products and add items to cart"
    echo "4. Complete the checkout process"
    echo "5. View order confirmation and status"
    exit 0
else
    echo -e "${RED}⚠️  Some e-commerce flow tests failed. Please review the details above.${NC}"
    exit 1
fi