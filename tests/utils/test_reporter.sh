#!/bin/bash
#
# Test Reporter Utility for Integration Tests
#
# Provides functions for formatting and reporting test results,
# generating summaries, and creating detailed test reports.
#

# Configuration
readonly REPORT_DIR="${PROJECT_ROOT:-$(pwd)}/tests/results"
readonly LOG_DIR="${PROJECT_ROOT:-$(pwd)}/tests/logs"

# Colors for console output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# Test result tracking
declare -a TEST_RESULTS=()
declare -i TOTAL_TESTS=0
declare -i PASSED_TESTS=0
declare -i FAILED_TESTS=0
declare -i SKIPPED_TESTS=0

# Report a test result
report_test_result() {
    local test_name="$1"
    local status="$2"  # PASS, FAIL, SKIP
    local message="$3"
    local duration="${4:-0}"
    local details="${5:-}"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Store result for later reporting
    local result_entry="${timestamp}|${test_name}|${status}|${message}|${duration}|${details}"
    TEST_RESULTS+=("$result_entry")
    
    # Update counters
    ((TOTAL_TESTS++))
    case "$status" in
        "PASS")
            ((PASSED_TESTS++))
            echo -e "${GREEN}✓${NC} ${test_name}: ${message}" | tee -a "${LOG_DIR}/test-results.log"
            ;;
        "FAIL")
            ((FAILED_TESTS++))
            echo -e "${RED}✗${NC} ${test_name}: ${message}" | tee -a "${LOG_DIR}/test-results.log"
            if [[ -n "$details" ]]; then
                echo -e "  ${RED}Details:${NC} $details" | tee -a "${LOG_DIR}/test-results.log"
            fi
            ;;
        "SKIP")
            ((SKIPPED_TESTS++))
            echo -e "${YELLOW}⊘${NC} ${test_name}: ${message}" | tee -a "${LOG_DIR}/test-results.log"
            ;;
        *)
            echo -e "${PURPLE}?${NC} ${test_name}: ${message} (unknown status: $status)" | tee -a "${LOG_DIR}/test-results.log"
            ;;
    esac
}

# Report test phase start
report_phase_start() {
    local phase_name="$1"
    local phase_description="$2"
    
    echo | tee -a "${LOG_DIR}/test-results.log"
    echo -e "${BLUE}===========================================${NC}" | tee -a "${LOG_DIR}/test-results.log"
    echo -e "${WHITE}Phase: ${phase_name}${NC}" | tee -a "${LOG_DIR}/test-results.log"
    if [[ -n "$phase_description" ]]; then
        echo -e "${CYAN}${phase_description}${NC}" | tee -a "${LOG_DIR}/test-results.log"
    fi
    echo -e "${BLUE}===========================================${NC}" | tee -a "${LOG_DIR}/test-results.log"
}

# Report test phase completion
report_phase_complete() {
    local phase_name="$1"
    local phase_status="$2"  # PASS, FAIL
    local phase_duration="${3:-0}"
    
    if [[ "$phase_status" == "PASS" ]]; then
        echo -e "${GREEN}Phase ${phase_name} completed successfully${NC} (${phase_duration}s)" | tee -a "${LOG_DIR}/test-results.log"
    else
        echo -e "${RED}Phase ${phase_name} failed${NC} (${phase_duration}s)" | tee -a "${LOG_DIR}/test-results.log"
    fi
    echo | tee -a "${LOG_DIR}/test-results.log"
}

# Generate summary statistics
generate_summary() {
    local start_time="$1"
    local end_time="$2"
    local total_duration=$((end_time - start_time))
    
    echo | tee -a "${LOG_DIR}/test-results.log"
    echo -e "${BLUE}===========================================${NC}" | tee -a "${LOG_DIR}/test-results.log"
    echo -e "${WHITE}Integration Test Summary${NC}" | tee -a "${LOG_DIR}/test-results.log"
    echo -e "${BLUE}===========================================${NC}" | tee -a "${LOG_DIR}/test-results.log"
    echo -e "Duration: ${total_duration} seconds" | tee -a "${LOG_DIR}/test-results.log"
    echo -e "Total Tests: ${TOTAL_TESTS}" | tee -a "${LOG_DIR}/test-results.log"
    echo -e "${GREEN}Passed: ${PASSED_TESTS}${NC}" | tee -a "${LOG_DIR}/test-results.log"
    echo -e "${RED}Failed: ${FAILED_TESTS}${NC}" | tee -a "${LOG_DIR}/test-results.log"
    echo -e "${YELLOW}Skipped: ${SKIPPED_TESTS}${NC}" | tee -a "${LOG_DIR}/test-results.log"
    
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        local success_rate=$(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc -l)
        echo -e "Success Rate: ${success_rate}%" | tee -a "${LOG_DIR}/test-results.log"
    fi
    
    echo | tee -a "${LOG_DIR}/test-results.log"
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed!${NC}" | tee -a "${LOG_DIR}/test-results.log"
        return 0
    else
        echo -e "${RED}❌ ${FAILED_TESTS} test(s) failed${NC}" | tee -a "${LOG_DIR}/test-results.log"
        return 1
    fi
}

# Generate detailed JSON report
generate_json_report() {
    local start_time="$1"
    local end_time="$2"
    local report_name="${3:-integration-test-report}"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="${REPORT_DIR}/${report_name}-$(date +%Y%m%d-%H%M%S).json"
    local total_duration=$((end_time - start_time))
    
    # Ensure report directory exists
    mkdir -p "$REPORT_DIR"
    
    # Start JSON structure
    cat > "$report_file" << EOF
{
  "report_metadata": {
    "generated_at": "$timestamp",
    "report_type": "integration_test_results",
    "version": "1.0"
  },
  "test_session": {
    "start_time": "$start_time",
    "end_time": "$end_time",
    "duration_seconds": $total_duration,
    "total_tests": $TOTAL_TESTS,
    "passed_tests": $PASSED_TESTS,
    "failed_tests": $FAILED_TESTS,
    "skipped_tests": $SKIPPED_TESTS,
    "success_rate": $(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc -l)
  },
  "test_results": [
EOF
    
    # Add test results
    local first_result=true
    for result in "${TEST_RESULTS[@]}"; do
        IFS='|' read -ra RESULT_PARTS <<< "$result"
        local test_timestamp="${RESULT_PARTS[0]}"
        local test_name="${RESULT_PARTS[1]}"
        local test_status="${RESULT_PARTS[2]}"
        local test_message="${RESULT_PARTS[3]}"
        local test_duration="${RESULT_PARTS[4]}"
        local test_details="${RESULT_PARTS[5]}"
        
        if [[ "$first_result" == false ]]; then
            echo "," >> "$report_file"
        fi
        first_result=false
        
        cat >> "$report_file" << EOF
    {
      "timestamp": "$test_timestamp",
      "name": "$test_name",
      "status": "$test_status",
      "message": "$test_message",
      "duration_seconds": $test_duration,
      "details": "$test_details"
    }
EOF
    done
    
    # Close JSON structure
    cat >> "$report_file" << EOF

  ],
  "summary": {
    "overall_status": "$([ $FAILED_TESTS -eq 0 ] && echo "PASSED" || echo "FAILED")",
    "recommendation": "$([ $FAILED_TESTS -eq 0 ] && echo "All tests passed successfully" || echo "Review failed tests and fix issues before deployment")"
  }
}
EOF
    
    echo "Detailed report generated: $report_file"
    return 0
}

# Generate HTML report
generate_html_report() {
    local start_time="$1"
    local end_time="$2"
    local report_name="${3:-integration-test-report}"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="${REPORT_DIR}/${report_name}-$(date +%Y%m%d-%H%M%S).html"
    local total_duration=$((end_time - start_time))
    
    # Ensure report directory exists
    mkdir -p "$REPORT_DIR"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integration Test Report - Project Zero App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .stat-label { color: #6c757d; margin-top: 5px; }
        .test-results { margin-top: 30px; }
        .test-item { padding: 15px; margin-bottom: 10px; border-radius: 6px; border-left: 4px solid; }
        .test-pass { background-color: #d4edda; border-left-color: #28a745; }
        .test-fail { background-color: #f8d7da; border-left-color: #dc3545; }
        .test-skip { background-color: #fff3cd; border-left-color: #ffc107; }
        .test-name { font-weight: bold; margin-bottom: 5px; }
        .test-message { color: #6c757d; }
        .test-details { margin-top: 10px; padding: 10px; background-color: rgba(0,0,0,0.05); border-radius: 4px; font-family: monospace; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Project Zero App - Integration Test Report</h1>
            <p>Generated on $timestamp</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-number">$TOTAL_TESTS</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #28a745;">$PASSED_TESTS</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #dc3545;">$FAILED_TESTS</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #ffc107;">$SKIPPED_TESTS</div>
                <div class="stat-label">Skipped</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${total_duration}s</div>
                <div class="stat-label">Duration</div>
            </div>
        </div>
        
        <div class="test-results">
            <h2>Test Results</h2>
EOF
    
    # Add test results
    for result in "${TEST_RESULTS[@]}"; do
        IFS='|' read -ra RESULT_PARTS <<< "$result"
        local test_timestamp="${RESULT_PARTS[0]}"
        local test_name="${RESULT_PARTS[1]}"
        local test_status="${RESULT_PARTS[2]}"
        local test_message="${RESULT_PARTS[3]}"
        local test_duration="${RESULT_PARTS[4]}"
        local test_details="${RESULT_PARTS[5]}"
        
        local css_class=""
        case "$test_status" in
            "PASS") css_class="test-pass" ;;
            "FAIL") css_class="test-fail" ;;
            "SKIP") css_class="test-skip" ;;
        esac
        
        cat >> "$report_file" << EOF
            <div class="test-item $css_class">
                <div class="test-name">$test_name</div>
                <div class="test-message">$test_message</div>
                <small>$test_timestamp | Duration: ${test_duration}s</small>
EOF
        
        if [[ -n "$test_details" ]]; then
            cat >> "$report_file" << EOF
                <div class="test-details">$test_details</div>
EOF
        fi
        
        echo "            </div>" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF
        </div>
    </div>
</body>
</html>
EOF
    
    echo "HTML report generated: $report_file"
    return 0
}

# Initialize reporting (create directories and clear previous logs)
init_reporting() {
    mkdir -p "$REPORT_DIR" "$LOG_DIR"
    
    # Clear previous logs
    > "${LOG_DIR}/test-results.log"
    
    # Reset counters
    TEST_RESULTS=()
    TOTAL_TESTS=0
    PASSED_TESTS=0
    FAILED_TESTS=0
    SKIPPED_TESTS=0
}

# Get current test statistics
get_test_stats() {
    echo "TOTAL:$TOTAL_TESTS|PASSED:$PASSED_TESTS|FAILED:$FAILED_TESTS|SKIPPED:$SKIPPED_TESTS"
}