#!/usr/bin/env python
"""
Temporary workaround for collation issues
"""

def apply_collation_workaround():
    """Apply temporary workaround for collation issues"""
    
    try:
        print("Applying temporary collation workaround...")
        
        # Test database connection first
        from app import create_app
        app = create_app()
        
        with app.app_context():
            conn = app.get_db_connection()
            try:
                with conn.cursor() as cursor:
                    # Check if tables exist and their collations
                    cursor.execute("""
                        SELECT table_name, table_collation 
                        FROM information_schema.tables 
                        WHERE table_schema = 'fin_guard'
                        ORDER BY table_name
                    """)
                    tables = cursor.fetchall()
                    
                    print(f"Found {len(tables)} tables in database:")
                    for table in tables:
                        print(f"  - {table['table_name']}: {table['table_collation']}")
                    
                    # Check for collation mismatches
                    collations = set(table['table_collation'] for table in tables)
                    if len(collations) > 1:
                        print(f"\n⚠️  Found {len(collations)} different collations:")
                        for collation in collations:
                            print(f"  - {collation}")
                        print("\nThis is likely the cause of the collation error.")
                        print("Please run: fix_collations.bat")
                        return False
                    else:
                        print(f"\n✓ All tables use the same collation: {collations.pop()}")
                        return True
                        
            finally:
                conn.close()
                
    except Exception as e:
        print(f"✗ Error checking collations: {e}")
        return False

if __name__ == "__main__":
    success = apply_collation_workaround()
    if success:
        print("\n🎉 No collation issues detected!")
    else:
        print("\n❌ Collation issues found. Please run fix_collations.bat")
