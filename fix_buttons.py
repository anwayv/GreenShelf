#!/usr/bin/env python3
"""
Fix script for button functionality issues
"""

import os
from pathlib import Path

def fix_javascript_issues():
    """Fix common JavaScript issues that prevent buttons from working"""
    
    # Read the current index.html
    index_file = Path("app/templates/index.html")
    if not index_file.exists():
        print("❌ index.html not found")
        return False
    
    content = index_file.read_text()
    
    # Create a fixed version with better error handling
    fixed_content = content.replace(
        '// Blinkit search UI\n  document.addEventListener("DOMContentLoaded", function () {\n    const searchInput = document.getElementById("blinkit-search");\n    const searchBtn = document.getElementById("btn-blinkit-search");\n    const resultsEl = document.getElementById("blinkit-results");\n    const saveBtn = document.getElementById("save-item");\n    const selectedName = document.getElementById("selected_name");\n    const selectedQuery = document.getElementById("selected_query");\n    const csrfToken = document\n      .querySelector(\'meta[name="csrf-token"]\')\n      .getAttribute("content");',
        '''// Blinkit search UI
  document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM loaded, initializing search functionality...");
    
    const searchInput = document.getElementById("blinkit-search");
    const searchBtn = document.getElementById("btn-blinkit-search");
    const resultsEl = document.getElementById("blinkit-results");
    const saveBtn = document.getElementById("save-item");
    const selectedName = document.getElementById("selected_name");
    const selectedQuery = document.getElementById("selected_query");
    
    // Check if elements exist
    if (!searchInput || !searchBtn || !resultsEl || !saveBtn || !selectedName || !selectedQuery) {
      console.error("Required elements not found:", {
        searchInput: !!searchInput,
        searchBtn: !!searchBtn,
        resultsEl: !!resultsEl,
        saveBtn: !!saveBtn,
        selectedName: !!selectedName,
        selectedQuery: !!selectedQuery
      });
      return;
    }
    
    // Get CSRF token with error handling
    let csrfToken = "";
    try {
      const csrfMeta = document.querySelector('meta[name="csrf-token"]');
      if (csrfMeta) {
        csrfToken = csrfMeta.getAttribute("content");
        console.log("CSRF token found");
      } else {
        console.error("CSRF token not found in meta tag");
        // Try to get from form
        const csrfInput = document.querySelector('input[name="csrf_token"]');
        if (csrfInput) {
          csrfToken = csrfInput.value;
          console.log("CSRF token found in form input");
        }
      }
    } catch (error) {
      console.error("Error getting CSRF token:", error);
    }
    
    if (!csrfToken) {
      console.error("No CSRF token available - buttons may not work");
    }'''
    )
    
    # Add better error handling to the search function
    fixed_content = fixed_content.replace(
        '    function doSearch() {\n      const q = (searchInput.value || "").trim();\n      if (!q) return;\n      saveBtn.disabled = true;\n      selectedName.value = "";\n      selectedQuery.value = "";\n      resultsEl.innerHTML = \'<div class="text-muted">Searching...</div>\';\n      fetch("/products/search", {\n        method: "POST",\n        headers: {\n          "Content-Type": "application/json",\n          "X-CSRFToken": csrfToken,\n        },\n        body: JSON.stringify({ q }),\n      })\n        .then((r) => r.json())\n        .then((data) => {\n          if (data.error) {\n            resultsEl.innerHTML = `<div class="text-danger">${data.error}</div>`;\n          } else {\n            renderResults(data.products);\n          }\n        })\n        .catch((err) => {\n          resultsEl.innerHTML = `<div class="text-danger">${err}</div>`;\n        });\n    }',
        '''    function doSearch() {
      const q = (searchInput.value || "").trim();
      if (!q) {
        console.log("No search query provided");
        return;
      }
      
      if (!csrfToken) {
        resultsEl.innerHTML = '<div class="text-danger">CSRF token missing. Please refresh the page.</div>';
        return;
      }
      
      console.log("Searching for:", q);
      saveBtn.disabled = true;
      selectedName.value = "";
      selectedQuery.value = "";
      resultsEl.innerHTML = '<div class="text-muted">Searching...</div>';
      
      fetch("/products/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ q }),
      })
        .then((r) => {
          if (!r.ok) {
            throw new Error(`HTTP ${r.status}: ${r.statusText}`);
          }
          return r.json();
        })
        .then((data) => {
          console.log("Search response:", data);
          if (data.error) {
            resultsEl.innerHTML = `<div class="text-danger">Error: ${data.error}</div>`;
          } else {
            renderResults(data.products);
          }
        })
        .catch((err) => {
          console.error("Search error:", err);
          resultsEl.innerHTML = `<div class="text-danger">Search failed: ${err.message}</div>`;
        });
    }'''
    )
    
    # Add error handling to the event listeners
    fixed_content = fixed_content.replace(
        '    if (searchBtn && searchInput) {\n      searchBtn.addEventListener("click", doSearch);\n      searchInput.addEventListener("keydown", (e) => {\n        if (e.key === "Enter") {\n          e.preventDefault();\n          doSearch();\n        }\n      });\n    }',
        '''    if (searchBtn && searchInput) {
      console.log("Adding event listeners for search functionality");
      searchBtn.addEventListener("click", (e) => {
        e.preventDefault();
        console.log("Search button clicked");
        doSearch();
      });
      searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          console.log("Enter key pressed in search");
          doSearch();
        }
      });
    } else {
      console.error("Search button or input not found - search functionality disabled");
    }
    
    // Add form submission debugging
    const forms = document.querySelectorAll("form");
    forms.forEach((form, index) => {
      form.addEventListener("submit", (e) => {
        console.log(`Form ${index} submitted:`, form.action || "no action");
      });
    });
    
    console.log("Search functionality initialized successfully");'''
    )
    
    # Write the fixed content back
    index_file.write_text(fixed_content)
    print("✅ Fixed JavaScript issues in index.html")
    return True

def check_flask_config():
    """Check if Flask configuration is correct"""
    print("🔍 Checking Flask configuration...")
    
    # Check if CSRF is properly configured
    init_file = Path("app/__init__.py")
    if init_file.exists():
        content = init_file.read_text()
        if "WTF_CSRF_ENABLED" in content or "CSRFProtect" in content:
            print("✅ CSRF protection appears to be configured")
        else:
            print("⚠️  CSRF protection might not be configured")
    
    # Check routes file
    routes_file = Path("app/routes.py")
    if routes_file.exists():
        content = routes_file.read_text()
        if "csrf_token" in content:
            print("✅ CSRF tokens are being used in routes")
        else:
            print("⚠️  CSRF tokens might not be used in routes")

def main():
    """Main fix function"""
    print("🔧 Fixing Button Functionality Issues...")
    print("=" * 50)
    
    # Fix JavaScript issues
    if fix_javascript_issues():
        print("✅ JavaScript fixes applied")
    else:
        print("❌ Failed to apply JavaScript fixes")
    
    # Check Flask configuration
    check_flask_config()
    
    print("\n🚀 Fixes Applied!")
    print("\n📋 What was fixed:")
    print("✅ Added better error handling for missing elements")
    print("✅ Added CSRF token validation")
    print("✅ Added console logging for debugging")
    print("✅ Added form submission debugging")
    print("✅ Added HTTP error handling")
    
    print("\n🔍 Next Steps:")
    print("1. Refresh your browser page")
    print("2. Open browser developer tools (F12)")
    print("3. Check the Console tab for any error messages")
    print("4. Try the search and save buttons again")
    
    print("\n🐛 If buttons still don't work:")
    print("1. Check browser console for specific error messages")
    print("2. Make sure Flask app is running without errors")
    print("3. Verify CSRF tokens are being generated")

if __name__ == "__main__":
    main()
