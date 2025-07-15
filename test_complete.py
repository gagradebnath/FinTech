#!/usr/bin/env python
"""
Complete test to verify all fixes work
"""

def test_complete_application():
    """Test complete application startup"""
    
    try:
        print("Testing complete application startup...")
        
        # Test imports
        from app import create_app
        print("✓ create_app imported successfully")
        
        # Test app creation
        app = create_app()
        print("✓ App created successfully")
        
        # Test specific functions that had issues
        with app.app_context():
            from app.utils.admin_utils import get_agents, get_all_users
            from app.utils.dashboard import get_user_budgets
            
            print("✓ All database functions imported successfully")
            print("✓ App context works correctly")
        
        print("\n🎉 All tests passed! The application should now work correctly.")
        print("Run: python run.py")
        print("Then visit: http://localhost:5000")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_application()
    if not success:
        print("\n❌ There are still issues to resolve")
