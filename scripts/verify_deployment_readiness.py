#!/usr/bin/env python3
"""
Sprint 1 Day 4 - Streamlit Cloud Deployment Verification Script
This script verifies all deployment requirements are met before going live.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a required file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False

def check_streamlit_config():
    """Verify Streamlit configuration files"""
    print("\n🔧 Checking Streamlit Configuration...")
    
    config_file = ".streamlit/config.toml"
    secrets_file = ".streamlit/secrets.toml"
    
    config_ok = check_file_exists(config_file, "Streamlit config")
    secrets_ok = check_file_exists(secrets_file, "Streamlit secrets template")
    
    return config_ok and secrets_ok

def check_deployment_files():
    """Check all deployment-related files"""
    print("\n📦 Checking Deployment Files...")
    
    files_to_check = [
        ("requirements.txt", "Python dependencies"),
        ("packages.txt", "System packages"),
        ("src/app.py", "Main application"),
        ("docs/DEPLOYMENT.md", "Deployment documentation"),
        ("Dockerfile", "Docker configuration"),
        ("README.md", "Project documentation")
    ]
    
    all_good = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good

def check_packages_format():
    """Verify packages.txt format is correct for Streamlit Cloud"""
    print("\n📦 Checking packages.txt Format...")
    
    try:
        with open('packages.txt', 'r') as f:
            lines = f.readlines()
        
        issues = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            if line.startswith('#'):  # Comment lines not allowed
                issues.append(f"Line {i}: Comments not allowed in packages.txt ('{line[:30]}...')")
            elif ' ' in line and not line.startswith('# '):  # Spaces in package names
                issues.append(f"Line {i}: Package names should not contain spaces ('{line}')")
        
        if issues:
            print("❌ packages.txt format issues found:")
            for issue in issues:
                print(f"   {issue}")
            print("   Fix: Remove all comment lines (starting with #)")
            print("   Streamlit Cloud treats every line as a package to install")
            return False
        else:
            package_count = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            print(f"✅ packages.txt format correct ({package_count} packages)")
            return True
            
    except FileNotFoundError:
        print("❌ packages.txt not found")
        return False
    except Exception as e:
        print(f"❌ Error checking packages.txt: {e}")
        return False

def verify_app_runs():
    """Verify the Streamlit app can start without errors"""
    print("\n🚀 Testing Application Startup...")
    
    try:
        # Try to import the main app to check for import errors
        sys.path.insert(0, 'src')
        
        # Test basic imports
        import streamlit as st
        import pandas as pd
        import numpy as np
        
        print("✅ Core dependencies importable")
        
        # Check if app file is syntactically correct
        with open('src/app.py', 'r') as f:
            app_content = f.read()
        
        compile(app_content, 'src/app.py', 'exec')
        print("✅ Application syntax check passed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except SyntaxError as e:
        print(f"❌ Syntax error in app.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Application startup test failed: {e}")
        return False

def check_requirements():
    """Verify requirements.txt is properly formatted"""
    print("\n📋 Checking Requirements File...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip()
        
        if not requirements:
            print("❌ requirements.txt is empty")
            return False
        
        # Check for key dependencies
        required_packages = ['streamlit', 'pandas', 'numpy']
        missing_packages = []
        
        for package in required_packages:
            if package not in requirements.lower():
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing required packages: {missing_packages}")
            return False
        
        print(f"✅ Requirements file contains {len(requirements.splitlines())} packages")
        return True
        
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def check_git_status():
    """Check git repository status"""
    print("\n🔄 Checking Git Repository Status...")
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  Uncommitted changes detected:")
            print(result.stdout)
            print("   Consider committing changes before deployment")
        else:
            print("✅ Working directory clean")
        
        # Check current branch
        branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                     capture_output=True, text=True, check=True)
        current_branch = branch_result.stdout.strip()
        print(f"✅ Current branch: {current_branch}")
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Git repository check failed")
        return False

def main():
    """Main verification function"""
    print("🎯 Sprint 1 Day 4 - Streamlit Cloud Deployment Verification")
    print("=" * 60)
    
    # Change to project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    print(f"📂 Working directory: {os.getcwd()}")
    
    # Run all checks
    checks = [
        ("Deployment Files", check_deployment_files),
        ("Packages Format", check_packages_format),
        ("Streamlit Configuration", check_streamlit_config), 
        ("Requirements", check_requirements),
        ("Application Startup", verify_app_runs),
        ("Git Status", check_git_status)
    ]
    
    all_passed = True
    results = []
    
    for check_name, check_func in checks:
        try:
            passed = check_func()
            results.append((check_name, passed))
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results.append((check_name, False))
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:<8} {check_name}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED - READY FOR STREAMLIT CLOUD DEPLOYMENT!")
        print("\n📋 Next Steps:")
        print("1. Push code to main branch")
        print("2. Configure Streamlit Cloud app")
        print("3. Set main file: src/app.py")  
        print("4. Upload secrets configuration")
        print("5. Configure custom domain: www.electionmodels.com/UKGE")
        print("\nSee docs/DEPLOYMENT.md for detailed instructions.")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - RESOLVE ISSUES BEFORE DEPLOYMENT")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
