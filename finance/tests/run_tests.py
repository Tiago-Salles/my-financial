#!/usr/bin/env python
"""
Test runner script for the finance app.
This script provides utilities to run tests with different configurations.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def run_tests_with_coverage(test_pattern=None, coverage=True, verbose=False):
    """
    Run tests with optional coverage reporting.
    
    Args:
        test_pattern (str): Pattern to match test files
        coverage (bool): Whether to run with coverage
        verbose (bool): Whether to run in verbose mode
    """
    # Change to the project directory
    os.chdir(project_root)
    
    # Build the test command
    cmd = ['python', 'manage.py', 'test']
    
    if test_pattern:
        cmd.append(f'finance.tests.{test_pattern}')
    else:
        cmd.append('finance.tests')
    
    if verbose:
        cmd.append('-v')
        cmd.append('2')
    
    # Add coverage if requested
    if coverage:
        try:
            import coverage
            cmd = ['coverage', 'run', '--source=finance'] + cmd[1:]
        except ImportError:
            print("Warning: coverage not installed. Running tests without coverage.")
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Run the tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # Generate coverage report if coverage was used
    if coverage and result.returncode == 0:
        try:
            subprocess.run(['coverage', 'report'], check=True)
            subprocess.run(['coverage', 'html'], check=True)
            print("\nCoverage report generated in htmlcov/")
        except subprocess.CalledProcessError:
            print("Warning: Could not generate coverage report.")
    
    return result.returncode

def run_specific_test_suite(suite_name):
    """Run a specific test suite."""
    suites = {
        'models': 'test_models',
        'serializers': 'test_serializers', 
        'views': 'test_views',
        'factories': 'test_factories',
        'integration': 'test_integration',
        'all': None
    }
    
    if suite_name not in suites:
        print(f"Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(suites.keys())}")
        return 1
    
    pattern = suites[suite_name]
    return run_tests_with_coverage(pattern, coverage=True, verbose=True)

def run_performance_tests():
    """Run performance tests."""
    print("Running performance tests...")
    return run_tests_with_coverage('test_integration.PerformanceIntegrationTest', coverage=False, verbose=True)

def run_integration_tests():
    """Run integration tests."""
    print("Running integration tests...")
    return run_tests_with_coverage('test_integration', coverage=True, verbose=True)

def run_unit_tests():
    """Run unit tests."""
    print("Running unit tests...")
    return run_tests_with_coverage('test_models', coverage=True, verbose=True)

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description='Run finance app tests')
    parser.add_argument('--suite', choices=['models', 'serializers', 'views', 'factories', 'integration', 'all'],
                       help='Specific test suite to run')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests')
    parser.add_argument('--unit', action='store_true',
                       help='Run unit tests only')
    parser.add_argument('--no-coverage', action='store_true',
                       help='Run tests without coverage')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.performance:
        return run_performance_tests()
    elif args.unit:
        return run_unit_tests()
    elif args.suite:
        return run_specific_test_suite(args.suite)
    else:
        # Run all tests by default
        return run_tests_with_coverage(coverage=not args.no_coverage, verbose=args.verbose)

if __name__ == '__main__':
    sys.exit(main()) 