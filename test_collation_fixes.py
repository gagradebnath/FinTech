#!/usr/bin/env python
"""
Test script to verify collation fixes work correctly
"""

def test_collation_fixes():
    """Test functions that had collation issues"""
    
    try:
        print("Testing collation fixes...")
        
        # Test the specific function that was failing
        from app.utils.admin_utils import get_all_frauds
        print("✓ get_all_frauds function imported successfully")
        
        # Test with app context
        from app import create_app
        app = create_app()
        
        with app.app_context():
            try:
                # Test the function that was causing collation errors
                result = get_all_frauds(limit=5)
                print(f"✓ get_all_frauds executed successfully, returned {len(result)} records")
                
                # Test other functions that might have similar issues
                from app.utils.admin_utils import get_all_users, get_agents
                users = get_all_users()
                agents = get_agents()
                
                print(f"✓ get_all_users executed successfully, returned {len(users)} users")
                print(f"✓ get_agents executed successfully, returned {len(agents)} agents")
                
            except Exception as e:
                print(f"✗ Database operation failed: {e}")
                if "collation" in str(e).lower():
                    print("   → This is still a collation issue. Please run fix_collations.bat")
                    return False
                else:
                    print("   → This might be a different database issue.")
                    return False
        
        print("\nAll collation-sensitive functions working correctly! ✓")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ General error: {e}")
        return False

if __name__ == "__main__":
    success = test_collation_fixes()
    if success:
        print("\n🎉 Collation fixes are working correctly!")
        print("The application should now work without collation errors.")
    else:
        print("\n❌ Collation issues still exist.")
        print("Please run: fix_collations.bat")
        print("Then try running the application again.")
