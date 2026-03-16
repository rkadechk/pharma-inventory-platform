@echo off
REM Test runner script for Pharma Inventory Platform (Windows)
REM Supports: pytest with coverage reporting and multiple execution modes

setlocal enabledelayedexpansion

REM Set project root
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

echo.
echo ==========================================
echo Pharma Inventory Platform - Test Runner
echo ==========================================
echo.

REM Parse arguments
set TEST_MODE=%1
set VERBOSE=%2

if "%TEST_MODE%"=="" set TEST_MODE=all
if "%VERBOSE%"=="" set VERBOSE=off

REM Create reports directory
if not exist test_reports mkdir test_reports
if not exist htmlcov mkdir htmlcov

echo Test Mode: %TEST_MODE%
echo Verbose: %VERBOSE%
echo.

REM Main execution
goto %TEST_MODE% 2>nul
echo Unknown mode: %TEST_MODE%
echo Valid modes: unit, integration, performance, quick, all, coverage
exit /b 1

:unit
echo [UNIT TESTS] Running unit tests only...
python -m pytest tests/unit -v --tb=short ^
    --cov=agents --cov=validators ^
    --cov-report=html:htmlcov --cov-report=term-missing
if errorlevel 1 exit /b 1
echo.
goto success

:integration
echo [INTEGRATION TESTS] Running integration tests only...
python -m pytest tests/integration -v --tb=short ^
    --cov=agents --cov=validators ^
    --cov-report=html:htmlcov --cov-report=term-missing
if errorlevel 1 exit /b 1
echo.
goto success

:performance
echo [PERFORMANCE TESTS] Running performance tests only...
python -m pytest tests -m "performance" -v --tb=short
if errorlevel 1 exit /b 1
echo.
goto success

:quick
echo [QUICK TEST] Running quick tests only (unit, no slow)...
python -m pytest tests/unit -m "not slow" -v --tb=short ^
    --cov=agents --cov=validators ^
    --cov-report=html:htmlcov --cov-report=term-missing
if errorlevel 1 exit /b 1
echo.
goto success

:all
echo [ALL TESTS] Running all tests...
echo.

echo [UNIT TESTS] Running unit tests...
python -m pytest tests/unit -v --tb=short ^
    --cov=agents --cov=validators ^
    --cov-report=html:htmlcov --cov-report=term-missing
if errorlevel 1 exit /b 1
echo.

echo [INTEGRATION TESTS] Running integration tests...
python -m pytest tests/integration -v --tb=short ^
    --cov=agents --cov=validators ^
    --cov-report=html:htmlcov --cov-report=term-missing
if errorlevel 1 exit /b 1
echo.

echo [PERFORMANCE TESTS] Running performance tests (optional)...
python -m pytest tests -m "performance" -v --tb=short
REM Don't fail if performance tests fail
echo.
goto success

:coverage
echo [COVERAGE] Running tests with detailed coverage report...
python -m pytest tests ^
    --cov=agents --cov=validators ^
    --cov-report=html:htmlcov ^
    --cov-report=term-missing ^
    --cov-report=xml ^
    --cov-fail-under=85 ^
    -v --tb=short
if errorlevel 1 exit /b 1
echo.
echo Coverage report generated in htmlcov/index.html
goto success

:success
echo.
echo ==========================================
echo Test Run Complete
echo ==========================================
echo.
echo Coverage Report: htmlcov/index.html
echo Test Results: Check output above
echo.
exit /b 0
