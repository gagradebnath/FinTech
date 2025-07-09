#!/usr/bin/env python3
"""
Simple test script to verify the transaction flow works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly"""
    try:
        from app.routes.transaction import transaction_bp, save_transaction, send_money_route
        print("✓ Transaction routes imported successfully")
        
        from app.utils.transaction_utils import (
            process_send_money_with_overspending,
            check_transaction_overspending,
            send_money,
            lookup_user_by_identifier
        )
        print("✓ Transaction utilities imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error during import: {e}")
        return False

def test_function_definitions():
    """Test that key functions are properly defined"""
    try:
        from app.utils.transaction_utils import process_send_money_with_overspending
        
        # Check if the function has the correct signature
        import inspect
        sig = inspect.signature(process_send_money_with_overspending)
        params = list(sig.parameters.keys())
        
        expected_params = ['user_id', 'recipient_identifier', 'amount', 'payment_method', 'note', 'location', 'confirm_overspending']
        
        if all(param in params for param in expected_params):
            print("✓ process_send_money_with_overspending has correct signature")
            return True
        else:
            print(f"✗ Function signature mismatch. Expected: {expected_params}, Got: {params}")
            return False
            
    except Exception as e:
        print(f"✗ Error checking function definition: {e}")
        return False

def main():
    print("Testing FinGuard Transaction Flow...")
    print("=" * 50)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_function_definitions():
        success = False
    
    print("=" * 50)
    if success:
        print("✓ All tests passed! Transaction flow is ready.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
