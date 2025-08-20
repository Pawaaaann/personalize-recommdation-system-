#!/usr/bin/env python3
"""
Test script to diagnose and fix project setup issues.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all required modules can be imported."""
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import fastapi
        print("✅ fastapi imported successfully")
    except ImportError as e:
        print(f"❌ fastapi import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ uvicorn import failed: {e}")
        return False
    
    return True

def test_project_structure():
    """Test if project structure is correct."""
    required_paths = [
        "src/edurec",
        "src/edurec/api",
        "src/edurec/data",
        "src/edurec/models",
        "data",
        "data/courses.csv",
        "data/interactions.csv"
    ]
    
    for path in required_paths:
        full_path = Path(path)
        if full_path.exists():
            print(f"✅ {path} exists")
        else:
            print(f"❌ {path} missing")
            return False
    
    return True

def test_data_loading():
    """Test if data can be loaded properly."""
    try:
        from edurec.data.data_loader import DataLoader
        loader = DataLoader()
        
        courses = loader.load_courses()
        print(f"✅ Loaded {len(courses)} courses")
        
        interactions = loader.load_interactions()
        print(f"✅ Loaded {len(interactions)} interactions")
        
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def main():
    """Run all diagnostic tests."""
    print("🔍 Running EduRec diagnostic tests...\n")
    
    print("1. Testing imports...")
    imports_ok = test_imports()
    print()
    
    print("2. Testing project structure...")
    structure_ok = test_project_structure()
    print()
    
    if imports_ok and structure_ok:
        print("3. Testing data loading...")
        data_ok = test_data_loading()
        print()
        
        if data_ok:
            print("🎉 All tests passed! Project is ready to run.")
            return True
    
    print("❌ Some tests failed. Please fix the issues above.")
    return False

if __name__ == "__main__":
    main()
