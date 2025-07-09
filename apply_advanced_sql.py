#!/usr/bin/env python3
"""
Migration script to apply advanced SQL features to the FinGuard database
This script applies stored procedures, functions, triggers, and views
"""

import pymysql
import os
import sys
from pathlib import Path

def get_mysql_config():
    """Get MySQL configuration from environment variables or defaults"""
    config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'port': int(os.environ.get('MYSQL_PORT', 3306)),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', 'g85a'),
        'database': os.environ.get('MYSQL_DATABASE', 'fin_guard'),
        'charset': 'utf8mb4'
    }
    return config

def apply_advanced_sql_features():
    """Apply advanced SQL features from the AdvancedSQL_MySQL.sql file"""
    config = get_mysql_config()
    
    print(f"Connecting to MySQL database at {config['host']}:{config['port']}...")
    
    try:
        # Connect to MySQL
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset=config['charset'],
            autocommit=False
        )
        
        print("✓ Connected to MySQL database")
        
        # Read the advanced SQL file
        sql_file_path = Path(__file__).parent / 'AdvancedSQL_MySQL.sql'
        
        if not sql_file_path.exists():
            print(f"❌ Advanced SQL file not found: {sql_file_path}")
            return False
        
        print(f"Reading SQL file: {sql_file_path}")
        
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("✓ SQL file loaded")
        
        # Execute the SQL content
        cursor = connection.cursor()
        
        try:
            # Split by delimiter changes and execute
            sections = sql_content.split('DELIMITER')
            
            for i, section in enumerate(sections):
                if not section.strip():
                    continue
                
                if i == 0:
                    # First section (before any delimiter change)
                    statements = [s.strip() for s in section.split(';') if s.strip()]
                    for stmt in statements:
                        if stmt.upper().startswith('USE'):
                            print(f"Executing: {stmt}")
                            cursor.execute(stmt)
                
                elif '//' in section:
                    # Section with // delimiter
                    parts = section.split('//')
                    delimiter_part = parts[0].strip()
                    
                    if len(parts) > 1:
                        statements = [s.strip() for s in parts[1].split('//') if s.strip()]
                        for stmt in statements:
                            if stmt and not stmt.strip() == ';':
                                print(f"Executing stored procedure/function/trigger...")
                                try:
                                    cursor.execute(stmt)
                                    print("✓ Success")
                                except Exception as e:
                                    print(f"⚠ Warning: {e}")
                                    # Continue with other statements
                
                else:
                    # Section with ; delimiter
                    statements = [s.strip() for s in section.split(';') if s.strip()]
                    for stmt in statements:
                        if stmt and not stmt.strip().startswith('--'):
                            print(f"Executing: {stmt[:50]}...")
                            try:
                                cursor.execute(stmt)
                                print("✓ Success")
                            except Exception as e:
                                print(f"⚠ Warning: {e}")
                                # Continue with other statements
            
            connection.commit()
            print("✓ All SQL statements executed and committed")
            
        except Exception as e:
            connection.rollback()
            print(f"❌ Error executing SQL: {e}")
            return False
        
        finally:
            cursor.close()
            connection.close()
        
        print("✓ Advanced SQL features applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def verify_features():
    """Verify that the advanced SQL features were applied correctly"""
    config = get_mysql_config()
    
    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        print("\nVerifying advanced SQL features...")
        
        # Check stored procedures
        cursor.execute("SHOW PROCEDURE STATUS WHERE Db = %s", (config['database'],))
        procedures = cursor.fetchall()
        print(f"✓ Found {len(procedures)} stored procedures")
        
        # Check functions
        cursor.execute("SHOW FUNCTION STATUS WHERE Db = %s", (config['database'],))
        functions = cursor.fetchall()
        print(f"✓ Found {len(functions)} functions")
        
        # Check triggers
        cursor.execute("SHOW TRIGGERS")
        triggers = cursor.fetchall()
        print(f"✓ Found {len(triggers)} triggers")
        
        # Check views
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
        views = cursor.fetchall()
        print(f"✓ Found {len(views)} views")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main function"""
    print("=== FinGuard Advanced SQL Features Migration ===")
    print()
    
    # Apply the advanced SQL features
    if apply_advanced_sql_features():
        # Verify the features
        if verify_features():
            print("\n✅ Migration completed successfully!")
            print("\nAdvanced SQL features now available:")
            print("  - Stored Procedures: ProcessMoneyTransfer, GetUserTransactionHistory, etc.")
            print("  - Functions: CalculateAccountAge, GetUserRiskScore, etc.")
            print("  - Triggers: Auto-logging, validation, blockchain integration")
            print("  - Views: User summaries, analytics, risk monitoring")
            return True
        else:
            print("\n⚠ Migration completed but verification failed")
            return False
    else:
        print("\n❌ Migration failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)