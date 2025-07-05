# FinGuard MySQL Setup - Quick Start Guide

## 🚀 One-Command Setup

For the fastest setup, run the automated migration script:

```batch
migrate_to_mysql.bat
```

**The script will prompt you to choose:**
1. **Enter credentials interactively** (recommended for first-time setup)
2. **Use configuration file** (mysql_config.py for repeated setups)

**What this does:**
- ✅ Installs all required Python packages
- ✅ Prompts for your MySQL credentials securely
- ✅ Sets up MySQL environment variables or config file
- ✅ Creates the database with proper schema
- ✅ Inserts test data with sample accounts
- ✅ Runs validation tests
- ✅ Provides clear status updates

## 📋 Prerequisites

1. **MySQL Server 8.0+** installed and running
2. **Python 3.8+** 
3. **MySQL credentials** (username/password with database creation permissions)

## 🔐 Configuration Options

### Option 1: Interactive Setup (Recommended)
- Choose option 1 when prompted
- Enter your MySQL credentials when asked
- Credentials are stored as environment variables for the session only

### Option 2: Configuration File
- Choose option 2 when prompted
- Script creates `mysql_config.py` from template
- Edit the file with your credentials
- Rerun the script
- **Secure**: File is added to .gitignore automatically

## 🔧 Manual Setup (Alternative)

If you prefer manual control:

### 1. Install Dependencies
```bash
pip install PyMySQL cryptography Flask-SQLAlchemy
```

### 2. Configure MySQL Credentials

**Option A: Environment Variables**
```bash
set MYSQL_HOST=localhost
set MYSQL_USER=your_username
set MYSQL_PASSWORD=your_password
set MYSQL_DATABASE=fin_guard
```

**Option B: Configuration File**
```bash
copy mysql_config_template.py mysql_config.py
# Edit mysql_config.py with your credentials
```

### 3. Initialize Database
```bash
python seed_mysql.py
```

### 4. Start Application
```bash
python run.py
```

## 🔑 Default Login Credentials

| Role  | Username | Password |
|-------|----------|----------|
| Admin | admin    | admin    |
| Agent | agent    | agent    |
| User  | user     | user     |

## ✅ What's Fixed

This setup includes fixes for all known issues:

### 🕐 Datetime Handling
- **Fixed**: All Jinja2 datetime errors
- **Solution**: Custom filters (`format_date`, `format_time`, `format_datetime`)
- **Before**: `{{ timestamp.split(' ')[0] }}` ❌
- **After**: `{{ timestamp|format_date }}` ✅

### 💳 Transaction Types  
- **Fixed**: MySQL ENUM constraint errors
- **Valid Types**: Transfer, Deposit, Withdrawal, Payment, Refund
- **Functions**: Agent add money, cash out, user transfers all work

### 🔗 Database Connection
- **Enhanced**: Robust PyMySQL configuration
- **Features**: Proper error handling, Unicode support, connection pooling

## 🧪 Testing Your Setup

After setup, test these key features:

1. **Login**: Try all three account types
2. **Dashboard**: Check transaction history displays correctly
3. **Agent Functions**: Test add money and cash out
4. **User Transfers**: Send money between accounts
5. **Admin Panel**: Verify admin functions work

## 📚 Documentation

- `MIGRATION_GUIDE.md` - Detailed migration steps
- `FINAL_MIGRATION_STATUS.md` - Complete status report
- `TRANSACTION_TYPE_FIX.md` - Transaction ENUM fix details

## 🆘 Need Help?

If you encounter issues:

1. Check that MySQL service is running
2. Verify your MySQL credentials
3. Ensure Python packages are installed
4. Review error messages in terminal
5. Check the documentation files above

## 🎯 Next Steps

Once setup is complete:
1. Customize user accounts and data
2. Configure production MySQL settings
3. Set up proper environment variables for production
4. Implement additional security measures as needed

**The application should now run without any datetime or transaction type errors!**
