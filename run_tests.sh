#!/bin/bash
# Test runner script for Pharma Inventory Platform
# Supports: pytest with coverage reporting and multiple execution modes

set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Pharma Inventory Platform - Test Runner"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
TEST_MODE="${1:-all}"
VERBOSE="${2:-}"

# Create reports directory
mkdir -p test_reports
mkdir -p htmlcov

echo "Test Mode: $TEST_MODE"
echo "Verbose: ${VERBOSE:-off}"
echo ""

# Function to run tests
run_tests() {
    local test_type=$1
    local test_path=$2
    local markers=$3
    
    echo -e "${YELLOW}Running $test_type...${NC}"
    
    cmd="python -m pytest $test_path"
    
    if [ -n "$markers" ]; then
        cmd="$cmd -m \"$markers\""
    fi
    
    if [ -n "$VERBOSE" ]; then
        cmd="$cmd -vv"
    fi
    
    cmd="$cmd --tb=short --cov=agents --cov=validators --cov-report=html:htmlcov --cov-report=term-missing"
    
    eval $cmd
    
    echo -e "${GREEN}✓ $test_type passed${NC}"
    echo ""
}

# Execute based on mode
case $TEST_MODE in
    
    unit)
        echo "MODE: Running unit tests only"
        run_tests "Unit Tests" "tests/unit" "unit or not (integration or performance)"
        ;;
    
    integration)
        echo "MODE: Running integration tests only"
        run_tests "Integration Tests" "tests/integration" "integration"
        ;;
    
    performance)
        echo "MODE: Running performance tests only"
        run_tests "Performance Tests" "tests" "performance"
        ;;
    
    quick)
        echo "MODE: Quick test run (unit only, no slow tests)"
        run_tests "Quick Tests" "tests/unit" "unit and not slow"
        ;;
    
    all)
        echo "MODE: Running all tests"
        echo ""
        
        run_tests "Unit Tests" "tests/unit" "unit or not (integration or performance)"
        run_tests "Integration Tests" "tests/integration" "integration"
        
        echo -e "${YELLOW}Running Performance Tests (optional)...${NC}"
        python -m pytest tests -m "performance" -v --tb=short || true
        echo ""
        ;;
    
    coverage)
        echo "MODE: Running tests with detailed coverage report"
        python -m pytest tests --cov=agents --cov=validators \
            --cov-report=html:htmlcov \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-fail-under=85 \
            -v --tb=short
        
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    *)
        echo -e "${RED}Unknown mode: $TEST_MODE${NC}"
        echo "Valid modes: unit, integration, performance, quick, all, coverage"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=========================================="
echo "Test Run Complete"
echo "==========================================${NC}"
echo ""
echo "Coverage Report: htmlcov/index.html"
echo ""

exit 0
