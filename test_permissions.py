import sqlite3

def test_permissions():
    # Connect to the database
    conn = sqlite3.connect('fin_guard.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if perm_edit_expense_habit and perm_manage_budget exist
    cursor.execute("SELECT * FROM permissions WHERE name IN ('perm_edit_expense_habit', 'perm_manage_budget')")
    permissions = cursor.fetchall()
    
    print("--- Permissions Check ---")
    for perm in permissions:
        print(f"Permission found: {perm['name']} - {perm['description']}")
    
    if len(permissions) < 2:
        missing = []
        if not any(p['name'] == 'perm_edit_expense_habit' for p in permissions):
            missing.append('perm_edit_expense_habit')
        if not any(p['name'] == 'perm_manage_budget' for p in permissions):
            missing.append('perm_manage_budget')
        print(f"Missing permissions: {', '.join(missing)}")
    
    # Check role permissions for the user role
    cursor.execute("""
        SELECT p.name FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        JOIN roles r ON rp.role_id = r.id
        WHERE r.name = 'user'
    """)
    user_permissions = cursor.fetchall()
    
    print("\n--- User Role Permissions ---")
    for perm in user_permissions:
        print(f"- {perm['name']}")
    
    # Check if the key permissions exist for the user role
    required_perms = ['perm_send_money', 'perm_view_dashboard', 'perm_edit_profile', 
                     'perm_edit_expense_habit', 'perm_manage_budget']
    
    missing = []
    for req_perm in required_perms:
        if not any(p['name'] == req_perm for p in user_permissions):
            missing.append(req_perm)
    
    if missing:
        print(f"\nMissing permissions for user role: {', '.join(missing)}")
    else:
        print("\nAll required permissions exist for the user role.")
    
    conn.close()

if __name__ == "__main__":
    test_permissions()
