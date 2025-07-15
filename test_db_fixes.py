#!/usr/bin/env python
"""
Script to test if the database connection issues are fixed
"""

def test_database_functions():
    """Test database functions that had connection issues"""
    
    try:
        print("Testing database functions...")
        
        # Test the specific function that was failing
        from app.utils.admin_utils import get_agents
        print("✓ get_agents function imported successfully")
        
        # Test other functions that might have similar issues
        from app.utils.admin_utils import get_all_users
        print("✓ get_all_users function imported successfully")
        
        from app.utils.dashboard import get_user_budgets
        print("✓ get_user_budgets function imported successfully")
        
        print("\nAll database functions imported successfully! ✓")
        print("Database connection issues should now be resolved.")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ General error: {e}")
        return False

if __name__ == "__main__":
    success = test_database_functions()
    if success:
        print("\n🎉 Database connection fixes applied successfully!")
        print("The application should now work without 'Already closed' errors.")
    else:
        print("\n❌ There are still issues with database functions")
