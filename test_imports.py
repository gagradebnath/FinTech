#!/usr/bin/env python
"""
Test script to verify all imports work correctly
"""

def test_imports():
    """Test all imports to identify any missing functions"""
    
    try:
        print("Testing basic imports...")
        from app import create_app
        print("✓ create_app imported successfully")
        
        print("\nTesting route imports...")
        from app.routes import register_blueprints
        print("✓ register_blueprints imported successfully")
        
        print("\nTesting transaction utils imports...")
        from app.utils.transaction_utils import (
            get_user_by_id, 
            send_money, 
            lookup_user_by_identifier, 
            is_user_flagged_fraud
        )
        print("✓ All transaction utils functions imported successfully")
        
        print("\nTesting app creation...")
        app = create_app()
        print("✓ App created successfully")
        
        print("\nAll imports successful! ✓")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ General error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 Ready to start the application!")
        print("Run: python run.py")
    else:
        print("\n❌ Fix imports before starting the application")
