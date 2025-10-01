#!/usr/bin/env python3
"""
Test script to verify Green Shelf setup
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf',
        'selenium', 'python_dotenv', 'pillow', 'opencv_python',
        'pytesseract', 'requests', 'google_generativeai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('_', '-'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'app/__init__.py',
        'app/models.py',
        'app/routes.py',
        'app/auth.py',
        'app/recipes.py',
        'app/meal_planning.py',
        'app/receipts.py',
        'bot/green_shelf_bot.py',
        'config.py',
        'run.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n📁 Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def check_directories():
    """Check if required directories exist"""
    required_dirs = [
        'app/templates',
        'app/static',
        'uploads'
    ]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"⚠️  {dir_path}/ - will be created automatically")
    
    return True

def main():
    """Run all checks"""
    print("🛒 Green Shelf Setup Verification\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Required Files", check_files),
        ("Directories", check_directories)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All checks passed! Green Shelf is ready to run.")
        print("\n🚀 To start the application:")
        print("   python run.py")
        print("\n📖 Then open: http://localhost:5000")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n📚 See README.md for detailed setup instructions.")
    
    return all_passed

if __name__ == "__main__":
    main()


