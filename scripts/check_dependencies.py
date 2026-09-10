#!/usr/bin/env python3
"""Dependency security checker script.

This script checks for known vulnerabilities in Python dependencies
using pip-audit and safety tools.
"""

import subprocess
import sys


def run_pip_audit():
    """Run pip-audit to check for known vulnerabilities."""
    print("Running pip-audit...")
    try:
        result = subprocess.run(
            ["pip-audit", "--desc"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("pip-audit found vulnerabilities or failed to run")
            return False
        print("pip-audit: No vulnerabilities found")
        return True
    except FileNotFoundError:
        print("pip-audit not found. Install with: pip install pip-audit")
        return None


def run_safety():
    """Run safety to check for known security issues."""
    print("\nRunning safety...")
    try:
        result = subprocess.run(
            ["safety", "check"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("safety found vulnerabilities or failed to run")
            return False
        print("safety: No vulnerabilities found")
        return True
    except FileNotFoundError:
        print("safety not found. Install with: pip install safety")
        return None


def main():
    """Main function to run all dependency checks."""
    print("=" * 60)
    print("Dependency Security Check")
    print("=" * 60)
    
    pip_audit_result = run_pip_audit()
    safety_result = run_safety()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if pip_audit_result is None and safety_result is None:
        print("Neither pip-audit nor safety is installed.")
        print("Install them with: pip install pip-audit safety")
        sys.exit(1)
    
    if pip_audit_result and safety_result:
        print("All checks passed: No vulnerabilities found")
        sys.exit(0)
    else:
        print("Some checks failed. Review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
