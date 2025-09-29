#!/bin/bash
#
# Response Validation Utility for Integration Tests
#
# Provides functions to validate API responses including JSON structure,
# field validation, and content verification for testing APIs.
#

# Check if jq is available for JSON processing
check_jq_available() {
    if ! command -v jq &> /dev/null; then
        echo "ERROR: jq is required for JSON validation but not installed"
        return 1
    fi
    return 0
}

# Validate JSON structure
is_valid_json() {
    local json_string="$1"
    
    if ! check_jq_available; then
        return 1
    fi
    
    echo "$json_string" | jq empty 2>/dev/null
}

# Extract JSON field value
get_json_field() {
    local json_string="$1"
    local field_path="$2"
    
    if ! check_jq_available; then
        return 1
    fi
    
    echo "$json_string" | jq -r "$field_path" 2>/dev/null
}

# Check if JSON field exists
json_field_exists() {
    local json_string="$1"
    local field_path="$2"
    
    if ! check_jq_available; then
        return 1
    fi
    
    local value=$(echo "$json_string" | jq -r "$field_path" 2>/dev/null)
    [[ "$value" != "null" && "$value" != "" ]]
}

# Validate JSON field value
validate_json_field() {
    local json_string="$1"
    local field_path="$2"
    local expected_value="$3"
    
    if ! json_field_exists "$json_string" "$field_path"; then
        echo "FAILED: Field '$field_path' does not exist"
        return 1
    fi
    
    local actual_value=$(get_json_field "$json_string" "$field_path")
    
    if [[ "$actual_value" == "$expected_value" ]]; then
        echo "SUCCESS: Field '$field_path' has expected value '$expected_value'"
        return 0
    else
        echo "FAILED: Field '$field_path' expected '$expected_value', got '$actual_value'"
        return 1
    fi
}

# Validate JSON field type
validate_json_field_type() {
    local json_string="$1"
    local field_path="$2"
    local expected_type="$3"  # string, number, boolean, array, object, null
    
    if ! check_jq_available; then
        return 1
    fi
    
    if ! json_field_exists "$json_string" "$field_path"; then
        echo "FAILED: Field '$field_path' does not exist"
        return 1
    fi
    
    local actual_type=$(echo "$json_string" | jq -r "type" 2>/dev/null)
    
    if [[ "$actual_type" == "$expected_type" ]]; then
        echo "SUCCESS: Field '$field_path' has expected type '$expected_type'"
        return 0
    else
        echo "FAILED: Field '$field_path' expected type '$expected_type', got '$actual_type'"
        return 1
    fi
}

# Validate health check response
validate_health_response() {
    local response_body="$1"
    local service_name="$2"
    
    if ! is_valid_json "$response_body"; then
        echo "FAILED: Health response is not valid JSON"
        return 1
    fi
    
    # Check for status field
    if ! json_field_exists "$response_body" ".status"; then
        echo "FAILED: Health response missing 'status' field"
        return 1
    fi
    
    local status=$(get_json_field "$response_body" ".status")
    if [[ "$status" == "healthy" || "$status" == "ok" || "$status" == "UP" ]]; then
        echo "SUCCESS: $service_name health check response valid"
        return 0
    else
        echo "FAILED: $service_name health status is '$status', expected healthy/ok/UP"
        return 1
    fi
}

# Validate authentication response
validate_auth_response() {
    local response_body="$1"
    local auth_type="$2"  # login, register, refresh
    
    if ! is_valid_json "$response_body"; then
        echo "FAILED: Auth response is not valid JSON"
        return 1
    fi
    
    case "$auth_type" in
        "login"|"register")
            # Should contain access_token and refresh_token
            if ! json_field_exists "$response_body" ".access_token"; then
                echo "FAILED: Auth response missing 'access_token' field"
                return 1
            fi
            
            if ! json_field_exists "$response_body" ".refresh_token"; then
                echo "FAILED: Auth response missing 'refresh_token' field"
                return 1
            fi
            
            echo "SUCCESS: Auth response contains required tokens"
            return 0
            ;;
        "refresh")
            # Should contain new access_token
            if ! json_field_exists "$response_body" ".access_token"; then
                echo "FAILED: Token refresh response missing 'access_token' field"
                return 1
            fi
            
            echo "SUCCESS: Token refresh response valid"
            return 0
            ;;
        *)
            echo "FAILED: Unknown auth type '$auth_type'"
            return 1
            ;;
    esac
}

# Validate API error response
validate_error_response() {
    local response_body="$1"
    local expected_status="$2"
    
    if ! is_valid_json "$response_body"; then
        echo "FAILED: Error response is not valid JSON"
        return 1
    fi
    
    # Check for error message or detail field
    if json_field_exists "$response_body" ".message" || json_field_exists "$response_body" ".detail" || json_field_exists "$response_body" ".error"; then
        echo "SUCCESS: Error response contains error information"
        return 0
    else
        echo "FAILED: Error response missing error information"
        return 1
    fi
}

# Validate pagination response
validate_pagination_response() {
    local response_body="$1"
    
    if ! is_valid_json "$response_body"; then
        echo "FAILED: Pagination response is not valid JSON"
        return 1
    fi
    
    # Check for common pagination fields
    local has_pagination=false
    
    if json_field_exists "$response_body" ".page" && json_field_exists "$response_body" ".total"; then
        has_pagination=true
    elif json_field_exists "$response_body" ".offset" && json_field_exists "$response_body" ".limit"; then
        has_pagination=true
    elif json_field_exists "$response_body" ".data" && validate_json_field_type "$response_body" ".data" "array"; then
        has_pagination=true
    fi
    
    if [[ "$has_pagination" == true ]]; then
        echo "SUCCESS: Response contains pagination information"
        return 0
    else
        echo "FAILED: Response missing pagination information"
        return 1
    fi
}

# Validate array response with minimum items
validate_array_response() {
    local response_body="$1"
    local min_items="${2:-0}"
    local array_path="${3:-.}"
    
    if ! is_valid_json "$response_body"; then
        echo "FAILED: Array response is not valid JSON"
        return 1
    fi
    
    if ! validate_json_field_type "$response_body" "$array_path" "array"; then
        echo "FAILED: Response field '$array_path' is not an array"
        return 1
    fi
    
    local item_count=$(echo "$response_body" | jq -r "${array_path} | length" 2>/dev/null)
    
    if [[ "$item_count" -ge "$min_items" ]]; then
        echo "SUCCESS: Array contains $item_count items (minimum $min_items required)"
        return 0
    else
        echo "FAILED: Array contains $item_count items, minimum $min_items required"
        return 1
    fi
}

# Validate JWT token format
validate_jwt_token() {
    local token="$1"
    
    # JWT should have 3 parts separated by dots
    local part_count=$(echo "$token" | tr '.' '\n' | wc -l)
    
    if [[ "$part_count" -eq 3 ]]; then
        echo "SUCCESS: JWT token has valid format"
        return 0
    else
        echo "FAILED: JWT token has invalid format (expected 3 parts, got $part_count)"
        return 1
    fi
}

# Validate date field format
validate_date_field() {
    local json_string="$1"
    local field_path="$2"
    local date_format="${3:-iso8601}"  # iso8601, unix, custom
    
    if ! json_field_exists "$json_string" "$field_path"; then
        echo "FAILED: Date field '$field_path' does not exist"
        return 1
    fi
    
    local date_value=$(get_json_field "$json_string" "$field_path")
    
    case "$date_format" in
        "iso8601")
            # Basic ISO 8601 format validation
            if [[ "$date_value" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2} ]]; then
                echo "SUCCESS: Date field '$field_path' has valid ISO 8601 format"
                return 0
            else
                echo "FAILED: Date field '$field_path' has invalid ISO 8601 format: $date_value"
                return 1
            fi
            ;;
        "unix")
            # Unix timestamp validation (should be a number)
            if [[ "$date_value" =~ ^[0-9]+$ ]]; then
                echo "SUCCESS: Date field '$field_path' has valid Unix timestamp format"
                return 0
            else
                echo "FAILED: Date field '$field_path' has invalid Unix timestamp format: $date_value"
                return 1
            fi
            ;;
        *)
            echo "FAILED: Unknown date format '$date_format'"
            return 1
            ;;
    esac
}

# Comprehensive response validation
validate_api_response() {
    local response_body="$1"
    local response_type="$2"  # health, auth, error, data, pagination
    local additional_params="$3"
    
    case "$response_type" in
        "health")
            validate_health_response "$response_body" "$additional_params"
            ;;
        "auth")
            validate_auth_response "$response_body" "$additional_params"
            ;;
        "error")
            validate_error_response "$response_body" "$additional_params"
            ;;
        "array")
            validate_array_response "$response_body" "$additional_params"
            ;;
        "pagination")
            validate_pagination_response "$response_body"
            ;;
        *)
            if is_valid_json "$response_body"; then
                echo "SUCCESS: Response is valid JSON"
                return 0
            else
                echo "FAILED: Response is not valid JSON"
                return 1
            fi
            ;;
    esac
}