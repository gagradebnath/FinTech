# FinGuard SQLite to MySQL Migration Guide v2.0

This guide will help you migrate your FinGuard application from SQLite to MySQL with all fixes for datetime handling and transaction type compatibility.

## ✅ Migration Status

**The migration is COMPLETE** with the following fixes:
- ✅ **Datetime handling**: Fixed all Jinja2 UndefinedError issues with custom filters
- ✅ **Transaction types**: Fixed MySQL ENUM compatibility for all transaction operations  
- ✅ **Database connectivity**: Robust PyMySQL configuration with proper error handling
- ✅ **Template compatibility**: All templates updated to use datetime filters instead of .split()

## Prerequisites

1. **MySQL Server**: Install MySQL 8.0 or later
2. **Python 3.8+**: Ensure you have a compatible Python version

## Quick Setup (Automated)

For the fastest setup, simply run the automated migration script:

```batch
migrate_to_mysql.bat
```

This script will:
1. Install all required Python packages
2. Set up environment variables
3. Create the MySQL database and schema
4. Insert sample data for testing
5. Run validation tests

## Manual Migration Steps

If you prefer manual setup or need to customize the process:

### 1. Install Required Python Packages

```bash
pip install PyMySQL cryptography Flask-SQLAlchemy
```

### 2. Set Up MySQL Database

1. **Install MySQL**: Download from https://dev.mysql.com/downloads/
2. **Start MySQL service**
3. **Create database user** (optional):

```sql
CREATE USER 'finguard_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON fin_guard.* TO 'finguard_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configure Database Connection

#### Option A: Environment Variables (Recommended)
```bash
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set MYSQL_USER=root
set MYSQL_PASSWORD=your_mysql_password
set MYSQL_DATABASE=fin_guard
```

#### Option B: Direct Configuration (seed_mysql.py)
Edit the `seed_mysql.py` file and update the `MYSQL_CONFIG` dictionary:

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'your_username',
    'password': 'your_password',
    'database': 'fin_guard',
    'charset': 'utf8mb4'
}
```

### 4. Run the MySQL Database Setup

Execute the MySQL seeding script to create the database, tables, and insert sample data:

```bash
python seed_mysql.py
```

This script will:
- ✅ Create the `fin_guard` database if it doesn't exist
- ✅ Create all tables with proper MySQL syntax and ENUM constraints
- ✅ Insert dummy data for testing (admin, agent, user accounts)
- ✅ Create sample transactions with valid ENUM types
- ✅ Set up proper foreign key relationships

### 5. Key Fixes Included

The migration includes several critical fixes:

#### ✅ **Datetime Handling**
- **Problem**: `UndefinedError: 'datetime.datetime object' has no attribute 'split'`
- **Solution**: Custom Jinja2 filters (`format_date`, `format_time`, `format_datetime`)
- **Files Fixed**: All templates now use `{{ timestamp|format_date }}` instead of `{{ timestamp.split(' ')[0] }}`

#### ✅ **Transaction Type ENUM**
- **Problem**: `Data truncated for column 'type' at row 1`
- **Solution**: Updated all transaction operations to use valid ENUM values
- **Valid Types**: `'Transfer'`, `'Deposit'`, `'Withdrawal'`, `'Payment'`, `'Refund'`

#### ✅ **Database Connection**
- **Enhancement**: Robust PyMySQL configuration with proper error handling
- **Features**: Connection pooling, Unicode support, proper charset handling
4. **Error handling**: Improved error handling with proper connection cleanup

### 6. Migrate Existing Data (Optional)

If you have existing SQLite data you want to migrate:

1. **Export SQLite data**:
```bash
### 6. Test the Migration

1. **Run permission tests**:
```bash
python test_permissions.py
```

2. **Test datetime filters** (if available):
```bash
python test_filters.py
```

3. **Start the application**:
```bash
python run.py
```

4. **Test core functionality**:
   - Login with default accounts (see credentials below)
   - Create transactions to test datetime handling
   - Use agent functions to test transaction types
   - Check admin dashboard for proper datetime display

## 🔑 Default Test Accounts

After migration, you can login with these test accounts:

| Role  | Username | Password | Permissions |
|-------|----------|----------|-------------|
| Admin | admin    | admin    | Full access to admin dashboard, user management |
| Agent | agent    | agent    | Add money, cash out, view transactions |
| User  | user     | user     | Send money, view dashboard, manage profile |

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Issue: "UndefinedError: 'datetime.datetime object' has no attribute 'split'"
- **Status**: ✅ **FIXED**
- **Solution**: Custom Jinja2 filters handle all datetime objects properly
- **Verify**: Check templates use `{{ timestamp|format_date }}` syntax

#### Issue: "Data truncated for column 'type' at row 1"
- **Status**: ✅ **FIXED** 
- **Solution**: All transaction types updated to valid ENUM values
- **Valid Values**: `'Transfer'`, `'Deposit'`, `'Withdrawal'`, `'Payment'`, `'Refund'`

#### Issue: MySQL connection errors
- **Check**: MySQL service is running
- **Check**: Credentials in config are correct
- **Check**: Database `fin_guard` exists
- **Check**: User has proper permissions

#### Issue: Missing data after migration
- **Solution**: Run `python seed_mysql.py` to recreate sample data
- **Note**: This will reset all data to default test accounts
- Added foreign key constraints with proper referential actions
- Used `ENUM` type for transaction types
- Added `ENGINE=InnoDB` and charset specifications

### Application Code Changes
- Replaced `sqlite3` with `pymysql`
- Updated SQL parameter placeholders from `?` to `%s`
- Added proper connection context management using `with conn.cursor() as cursor:`
- Updated timestamp handling (`NOW()` instead of `CURRENT_TIMESTAMP`)
- Improved error handling and connection cleanup

### Configuration Changes
- Added MySQL-specific configuration options
- Support for environment-based configuration
- Flexible connection parameters

## Troubleshooting

### Common Issues

1. **Connection refused**: Make sure MySQL service is running
2. **Access denied**: Check username/password and user privileges
3. **Database doesn't exist**: The script should create it automatically, but you can create it manually:
   ```sql
   CREATE DATABASE fin_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

4. **Import errors**: Install required packages:
   ```bash
   pip install PyMySQL cryptography
   ```

### Performance Optimization

For production use, consider:
1. **Connection pooling**: Implement connection pooling for better performance
2. **Indexes**: The schema includes basic indexes, but you may want to add more based on usage patterns
3. **Configuration tuning**: Adjust MySQL configuration for your server specs

### Security Considerations

1. **Use environment variables** for database credentials
2. **Create dedicated database user** with minimal required privileges
3. **Enable SSL** for database connections in production
4. **Regular backups**: Set up automated database backups

## Rollback Plan

If you need to rollback to SQLite:
1. Keep your original SQLite database file as backup
2. The original SQLite-compatible code is preserved in `seed_sqlite.py`
3. Revert the application files to use SQLite connections

## Support

If you encounter issues during migration:
1. Check MySQL error logs
2. Verify all required packages are installed
3. Ensure database credentials are correct
4. Test connection with MySQL client tools first
