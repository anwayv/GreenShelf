#!/usr/bin/env python3
"""
Test script to verify Tesseract OCR installation
"""

import os
import sys
from pathlib import Path

def test_tesseract_installation():
    """Test if Tesseract is properly installed and accessible"""
    print("🔍 Testing Tesseract OCR Installation...")
    print("=" * 50)
    
    # Test 1: Check if pytesseract is installed
    try:
        import pytesseract
        print("✅ pytesseract module is installed")
    except ImportError:
        print("❌ pytesseract module not found")
        print("   Install with: pip install pytesseract")
        return False
    
    # Test 2: Check if tesseract executable is in PATH
    try:
        # Try to get tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract executable found - Version: {version}")
    except Exception as e:
        print(f"❌ Tesseract executable not found in PATH")
        print(f"   Error: {e}")
        print("\n🔧 Solutions:")
        print("   1. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   2. Add Tesseract to your PATH environment variable")
        print("   3. Or set the path manually in your code:")
        print("      pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        return False
    
    # Test 3: Check if tesseract can process a simple image
    try:
        # Create a simple test image with PIL
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Create a simple test image
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "TEST TEXT", fill='black')
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Test OCR
        text = pytesseract.image_to_string(img)
        print(f"✅ OCR test successful - Detected text: '{text.strip()}'")
        
    except Exception as e:
        print(f"⚠️  OCR test failed: {e}")
        print("   This might be due to image processing issues, but Tesseract is installed")
    
    print("\n🎉 Tesseract installation test completed!")
    return True

def check_receipt_processing_config():
    """Check the receipt processing configuration"""
    print("\n🔍 Checking Receipt Processing Configuration...")
    
    # Check if the receipt processing files exist
    receipt_files = [
        "app/receipts.py",
        "app/templates/receipts/upload.html"
    ]
    
    for file_path in receipt_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
    
    # Check if uploads directory exists
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        print(f"✅ Uploads directory exists: {uploads_dir.absolute()}")
    else:
        print(f"⚠️  Uploads directory missing, creating it...")
        uploads_dir.mkdir(exist_ok=True)
        print(f"✅ Created uploads directory: {uploads_dir.absolute()}")

if __name__ == "__main__":
    success = test_tesseract_installation()
    check_receipt_processing_config()
    
    if success:
        print("\n🚀 Receipt processing should now work!")
        print("Try uploading a receipt image again.")
    else:
        print("\n❌ Please fix the Tesseract installation issues above.")
