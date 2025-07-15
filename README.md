# FinGuard: Personal Finance Management Web App

> **🚀 INSTANT SETUP: Just run `setup.bat` → Open http://localhost:5000**  
> Login: admin/admin, agent/agent, or user/user

FinGuard is a comprehensive personal finance management web application with advanced PL/SQL optimizations, rollback functionality, modern UI, role-based access control, budget planning, and transaction management.

## 🚀 **ONE-CLICK SETUP**

**Just double-click:** `setup.bat`

The setup will prompt you for MySQL credentials, then everything happens automatically:
- ✅ Installs MySQL (if needed)
- ✅ Installs Python packages  
- 🔄 Creates fresh database (removes existing if found)
- 🔧 Updates app/config.py with your MySQL credentials
- ✅ Deploys comprehensive PL/SQL optimizations
- ✅ Adds test data and user accounts
- ✅ Starts the application

⚠️ **Note**: This will delete any existing `fin_guard` database for a clean installation.

## 💻 **Requirements**

- Windows OS
- Python 3.8+ (will be installed if missing)
- MySQL 5.7+ (will be installed if missing)
- Internet connection (for package installation)

**No need to install MySQL manually - the setup script handles it!**

## 🎯 **Test It Instantly**

After running `setup.bat`, login with these accounts:

| Username | Password | Role  |
|----------|----------|-------|
| admin    | admin    | Admin |
| agent    | agent    | Agent |
| user     | user     | User  |

Access: http://localhost:5000 (opens automatically)

## ✨ **Key Features**

### 🏦 **Core Banking Features**
- **� Enhanced Money Transfers**: Fraud detection, balance validation
- **🔄 Transaction Rollbacks**: 72-hour rollback window with audit trail
- **📊 Risk Assessment**: Real-time user risk scoring
- **🛡️ Fraud Protection**: Automatic fraud flagging and prevention

### 🎛️ **Advanced PL/SQL Features**
- **⚡ Stored Procedures**: 7 optimized procedures for core operations
- **� Functions**: 4 analytical functions for risk and spending analysis
- **👁️ Views**: 3 comprehensive views for reporting and monitoring
- **🔔 Triggers**: 3 audit triggers for automatic logging

### 💼 **Multi-Role System**
- **Admin Dashboard**: User management, system monitoring, fraud reports
- **Agent Dashboard**: Customer service, transaction assistance
- **User Dashboard**: Personal finance, budgets, transaction history

### 📱 **Modern Interface**
- **🌙 Dark Theme**: Professional dark mode interface
- **📱 Responsive Design**: Works on all devices
- **📊 Real-time Charts**: Interactive financial analytics
- **🔒 Security**: Role-based permissions, session management

## 🛠️ **What's Inside**

### 🏦 **Core Banking Operations**
- **💸 Enhanced Money Transfers**: Secure transfers with fraud detection
- **🔄 Transaction Rollbacks**: Undo transactions within 72 hours
- **📊 Budget Planning**: Create and manage personal budgets
- **📈 Transaction Analytics**: Real-time financial insights
- **🛡️ Fraud Protection**: Automatic fraud detection and reporting

### 👨‍💼 **Multi-Role Dashboards**
- **🔧 Admin Panel**: User management, system monitoring, fraud reports
- **🎯 Agent Tools**: Customer service, money operations, transaction assistance
- **👤 User Portal**: Personal finance, budgets, transaction history

### 📊 **Advanced Analytics**
- **📈 Risk Scoring**: AI-powered user risk assessment
- **💰 Spending Analysis**: Daily/weekly/monthly spending patterns
- **🔍 Audit Trails**: Complete transaction logging and monitoring
- **📋 Reporting**: Comprehensive financial reports

## 🗃️ **Database Features**

### 📦 **Stored Procedures**
- **`ProcessMoneyTransferEnhanced`**: Enhanced money transfer with fraud detection
- **`RollbackTransaction`**: Rollback completed transactions
- **`GetTransactionStatus`**: Check transaction status and rollback eligibility
- **`BackupUserBalance`**: Create user balance backups
- **`RestoreUserBalance`**: Restore user balance from backup
- **`AutoRollbackFailedTransactions`**: Auto-rollback failed transactions
- **`CleanupOldFraudReports`**: Clean up old fraud reports

### 🔧 **Functions**
- **`GetUserRiskScore`**: Calculate user risk score (0-100)
- **`GetUserDailySpending`**: Get daily spending amount
- **`IsWithinSpendingLimit`**: Check if user is within spending limits
- **`GetUserTransactionCount`**: Get transaction count for specified period

### 👁️ **Views**
- **`v_transaction_analytics`**: Comprehensive transaction analysis
- **`v_user_risk_analysis`**: User risk and spending analysis
- **`v_rollback_monitoring`**: Rollback eligibility monitoring

### 🔔 **Triggers**
- **`tr_transaction_balance_update`**: Auto-update balances on transactions
- **`tr_fraud_report_audit`**: Audit fraud report submissions
- **`tr_user_update_audit`**: Audit user account changes

## 📁 **Project Structure**

```
FinGuard/
├── setup.bat                      # 🚀 One-click setup script (run this!)
├── auto_setup.py                  # Automatic MySQL installation and setup
├── database_seed.py               # Database seeding with test data
├── run.py                         # Start the application
├── FinGuard_Complete_PL_SQL.sql   # 🆕 Complete PL/SQL optimizations
├── deploy_complete.bat            # Deploy all PL/SQL features
├── fix_collations.sql             # Fix database collation issues
├── app/                           # Main application code
│   ├── routes/                    # Web pages and API endpoints
│   ├── templates/                 # HTML templates
│   ├── static/                    # CSS, JavaScript, images
│   └── utils/                     # Business logic and database operations
└── DatabaseSchema_MySQL.sql       # MySQL database schema
```

## 🆘 **Need Help?**

### **Setup Issues**
- **MySQL installation fails**: The script will prompt to install manually from https://dev.mysql.com/downloads/
- **Permission denied**: Run `setup.bat` as administrator
- **Python not found**: Install Python 3.8+ from https://python.org
- **MySQL connection fails**: Double-check your MySQL credentials (host, port, username, password)
- **Collation errors**: Run `fix_collations.bat` to fix database collation issues

### **Application Issues**  
- **Can't login**: Use test accounts (admin/admin, agent/agent, user/user)
- **Page errors**: Restart by running `python run.py`
- **Missing data**: Rerun `setup.bat` to recreate sample data

### **Advanced Configuration**
- **Custom MySQL settings**: Edit `mysql_config_template.py` before running setup
- **Production deployment**: Set environment variables for database credentials
- **Development**: All source code is in the `app/` directory
## 🚀 **Quick Start**

1. **Double-click**: `setup.bat`
2. **Enter MySQL credentials**: When prompted (host, port, username, password)
3. **Wait**: Automatic setup completes (2-5 minutes)
4. **Access**: Browser opens to http://localhost:5000
5. **Login**: Use admin/admin, agent/agent, or user/user

## � **Manual Setup** (Optional)

If you prefer manual control:

```cmd
# Install dependencies
pip install PyMySQL cryptography Flask-SQLAlchemy

# Setup database and seed data
python auto_setup.py

# Start application
python run.py
```

## 🔑 **Demo Accounts**

All accounts start with 10,000 balance for testing:

| Role   | Username | Password | Features |
|--------|----------|----------|----------|
| Admin  | admin    | admin    | User management, admin dashboard |
| Agent  | agent    | agent    | Add money, cash out, agent dashboard |
| User   | user     | user     | Send money, budgets, profile |

## 💾 **Database (MySQL)**

- **Database**: MySQL 8.0+ (`fin_guard` database)
- **Schema**: `DatabaseSchema_MySQL.sql` with proper ENUM constraints
- **Setup**: Fully automated via `setup.bat`
- **Connection**: PyMySQL with robust error handling
- **Features**: 
  - ✅ Foreign key relationships
  - ✅ ENUM constraints for data integrity
  - ✅ Automatic installation and configuration
## 🏗️ **Built With**

- **Python Flask** - Web framework
- **MySQL** - Database  
- **Bootstrap 5** - Modern UI
- **Chart.js** - Data visualization

## 💡 **What Makes It Special**

✅ **Fully Working**: All features tested and functional  
✅ **One-Click Setup**: Single script does everything automatically
✅ **Modern Design**: Dark theme, responsive layout  
✅ **Real-World Ready**: Role permissions, security features  
✅ **Zero Configuration**: Automatic MySQL installation and setup  

---

**Ready to explore personal finance management? Just run `setup.bat` and start in under 5 minutes!**
