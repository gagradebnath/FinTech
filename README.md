# FinGuard: Personal Finance Management Web A### 🏦 **Co### 🎛️ **Advanced PL/SQL Features**
- **⚡ Stored Procedures**: 7 optimiz### 🔧 **Technical Implementation**
- **Database Integration**: Two dedicated blockchain tables
  - `blockchain`: Store blockchain blocks with hash chains
  - `blockchain_transactions`: Store blockchain-specific transaction data
- **Python Implementation**: Complete blockchain classes and utilities
- **API Endpoints**: REST APIs for blockchain verification and analytics
- **Real-time Processing**: Blockchain validation during transaction processing

### 🗄️ **Complete Database Schema**

FinGuard uses a comprehensive MySQL database with 14 core tables:

#### **Core Tables**
- **`users`**: User account information with balance tracking
- **`roles`**: Role-based access control (USER, ADMIN, AGENT)
- **`permissions`**: System permissions and capabilities
- **`role_permissions`**: Role-permission mappings
- **`transactions`**: All financial transactions with audit trail
- **`contact_info`**: User contact information (email, phone)
- **`addresses`**: User address information

#### **Blockchain Tables**
- **`blockchain`**: Immutable blockchain blocks with hash chains
- **`blockchain_transactions`**: Blockchain-specific transaction data

#### **Security & Fraud Tables**
- **`fraud_list`**: Fraud reports and investigations
- **`user_passwords`**: Secure password hashes
- **`admin_logs`**: Complete audit trail of all actions

#### **Budget & Finance Tables**
- **`budgets`**: User budget planning
- **`budget_expense_categories`**: Budget expense categories
- **`budget_expense_items`**: Individual budget items
- **`user_expense_habit`**: User spending patterns and habits

#### **Database Features**
- **Foreign Key Constraints**: Complete referential integrity
- **Indexes**: Optimized queries with strategic indexing
- **Triggers**: Automatic validation and audit logging
- **Stored Procedures**: Complex operations with error handling
- **Functions**: Analytical functions for risk assessment

## 🗃️ **Database Features**ures for core operations
- **🔧 Functions**: 4 analytical functions for risk and spending analysis
- **👁️ Views**: 3 comprehensive views for reporting and monitoring
- **🔔 Triggers**: 4 audit triggers for automatic logging and fraud detection
- **🔗 Blockchain Integration**: Immutable transaction records with SHA-256 hashingnking Features**
- **💸 Enhanced Money Transfers**: Fraud detection, balance validation
- **🔄 Transaction Rollbacks**: 72-hour rollback window with audit trail
- **📊 Risk Assessment**: Real-time user risk scoring
- **🛡️ Fraud Protection**: Automatic fraud flagging and prevention
- **🔗 Blockchain Security**: SHA-256 blockchain for transaction integrity
- **🔐 Immutable Records**: Tamper-proof transaction history
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
- **🔗 Blockchain Security**: Immutable transaction records with SHA-256 hashing
- **🔐 Transaction Integrity**: Tamper-proof blockchain validation

### 👨‍💼 **Multi-Role Dashboards**
- **🔧 Admin Panel**: User management, system monitoring, fraud reports, blockchain analytics
- **🎯 Agent Tools**: Customer service, money operations, transaction assistance
- **👤 User Portal**: Personal finance, budgets, transaction history

### 📊 **Advanced Analytics**
- **📈 Risk Scoring**: AI-powered user risk assessment
- **💰 Spending Analysis**: Daily/weekly/monthly spending patterns
- **🔍 Audit Trails**: Complete transaction logging and monitoring
- **📋 Reporting**: Comprehensive financial reports
- **🔗 Blockchain Analytics**: Real-time blockchain integrity monitoring
- **🔐 Fraud Detection**: Advanced blockchain-based fraud detection

## � **Blockchain Implementation**

FinGuard features a complete blockchain implementation for transaction security and fraud detection:

### 🏗️ **Blockchain Architecture**
- **Block Class**: Immutable blocks with SHA-256 hashing
- **Genesis Block**: System-initialized first block
- **Chain Validation**: Complete blockchain integrity verification
- **Tamper Detection**: Automatic detection of blockchain manipulation

### 🔐 **Security Features**
- **SHA-256 Hashing**: Cryptographic security for each block
- **Immutable Records**: Tamper-proof transaction history
- **Chain Validation**: Real-time blockchain integrity checks
- **Fraud Detection**: Advanced fraud detection through blockchain analysis

### 📊 **Blockchain Analytics Dashboard**
- **Real-time Monitoring**: Live blockchain status and health
- **Block Statistics**: Total blocks, validation status, chain health
- **Fraud Reports**: Blockchain-based fraud detection results
- **Transaction Verification**: Verify individual transactions via blockchain

### 🛡️ **Fraud Detection via Blockchain**
- **Transaction Validation**: Every transaction validated against blockchain
- **Inconsistency Detection**: Automatic detection of blockchain inconsistencies
- **User Flagging**: Automatic fraud flagging based on blockchain analysis
- **Audit Trail**: Complete audit trail of all blockchain operations

### 🔧 **Technical Implementation**
- **Database Integration**: Two dedicated blockchain tables
  - `blockchain`: Store blockchain blocks with hash chains
  - `blockchain_transactions`: Store blockchain-specific transaction data
- **Python Implementation**: Complete blockchain classes and utilities
- **API Endpoints**: REST APIs for blockchain verification and analytics
- **Real-time Processing**: Blockchain validation during transaction processing

## �🗃️ **Database Features**

### 📦 **Stored Procedures**
- **`ProcessMoneyTransferEnhanced`**: Enhanced money transfer with fraud detection
- **`RollbackTransaction`**: Rollback completed transactions
- **`GetTransactionStatus`**: Check transaction status and rollback eligibility
- **`BackupUserBalance`**: Create user balance backups
- **`RestoreUserBalance`**: Restore user balance from backup
- **`AutoRollbackFailedTransactions`**: Auto-rollback failed transactions
- **`CleanupOldFraudReports`**: Clean up old fraud reports
- **`AddColumnIfNotExists`**: Dynamic database schema modifications

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
- **`tr_transaction_audit`**: Automatic transaction audit logging
- **`tr_balance_validation`**: Prevent negative balances and log changes
- **`tr_fraud_detection`**: Real-time fraud detection and flagging
- **`tr_user_registration`**: Handle new user registration tasks

### 🔗 **Blockchain Implementation**
- **`Block` Class**: Immutable blocks with SHA-256 hashing
- **`FinGuardBlockchain` Class**: Complete blockchain management
- **Blockchain Tables**: 
  - `blockchain`: Store blockchain blocks
  - `blockchain_transactions`: Store blockchain-specific transaction data
- **Fraud Detection**: Advanced blockchain-based fraud detection
- **Transaction Integrity**: Tamper-proof transaction validation
- **Real-time Monitoring**: Blockchain analytics and monitoring dashboard

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
├── DatabaseSchema_MySQL.sql       # MySQL database schema
├── app/                           # Main application code
│   ├── routes/                    # Web pages and API endpoints
│   │   ├── blockchain.py          # 🆕 Blockchain routes and analytics
│   │   ├── admin.py               # Admin dashboard
│   │   ├── agent.py               # Agent operations
│   │   ├── user.py                # User operations
│   │   └── fraud.py               # Fraud detection
│   ├── templates/                 # HTML templates
│   │   ├── blockchain_dashboard.html # 🆕 Blockchain monitoring dashboard
│   │   ├── admin_dashboard.html   # Admin interface
│   │   └── ...                    # Other templates
│   ├── static/                    # CSS, JavaScript, images
│   └── utils/                     # Business logic and database operations
│       ├── blockchain_utils.py    # 🆕 Complete blockchain implementation
│       ├── advanced_sql_utils.py  # Advanced SQL operations
│       ├── fraud_utils.py         # Fraud detection utilities
│       └── ...                    # Other utilities
└── PL_SQL_Documentation.md        # 🆕 Complete PL/SQL documentation
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
| Admin  | admin    | admin    | User management, admin dashboard, blockchain analytics |
| Agent  | agent    | agent    | Add money, cash out, agent dashboard |
| User   | user     | user     | Send money, budgets, profile |

### 🔗 **Blockchain Dashboard Access**
- **Admin Users**: Access full blockchain analytics at `/blockchain-dashboard`
- **Real-time Monitoring**: Live blockchain health and integrity status
- **Fraud Detection**: View blockchain-based fraud detection results
- **Transaction Verification**: Verify individual transactions via blockchain

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

✅ **Enterprise-Grade Security**: Complete blockchain implementation with SHA-256 hashing  
✅ **Advanced Fraud Detection**: Multi-layered fraud detection with automatic flagging  
✅ **Fully Working**: All features tested and functional including blockchain validation  
✅ **One-Click Setup**: Single script does everything automatically  
✅ **Modern Design**: Dark theme, responsive layout with blockchain analytics  
✅ **Real-World Ready**: Role permissions, security features, immutable audit trail  
✅ **Zero Configuration**: Automatic MySQL installation and setup  
✅ **Comprehensive Database**: 14 tables with stored procedures, functions, and triggers  
✅ **Complete Documentation**: Full database documentation in `/app/utils/README.md`  

### 🔐 **Security Features**
- **Blockchain Integrity**: Every transaction secured with SHA-256 blockchain
- **Immutable Records**: Tamper-proof transaction history
- **Fraud Detection**: Advanced fraud detection through blockchain analysis
- **Role-Based Access**: Multi-level permission system
- **Audit Trail**: Complete logging of all system actions
- **Password Security**: Bcrypt hashing with salt

### 📊 **Analytics & Monitoring**
- **Real-time Blockchain Analytics**: Live monitoring of blockchain health
- **Transaction Analytics**: Comprehensive transaction analysis
- **Risk Assessment**: AI-powered user risk scoring
- **Fraud Reports**: Detailed fraud investigation reports
- **System Monitoring**: Complete system health monitoring
- **Performance Metrics**: Database and application performance tracking  

---

**Ready to explore personal finance management with enterprise-grade blockchain security? Just run `setup.bat` and start in under 5 minutes!**

## 📚 **Complete Documentation**

### **Database Documentation**
- **`/app/utils/README.md`**: Complete database documentation including:
  - All 14 database tables with column descriptions
  - Stored procedures, functions, and triggers
  - Common database queries used throughout the application
  - Blockchain implementation details
  - Security features and fraud detection mechanisms

### **PL/SQL Documentation**
- **`PL_SQL_Documentation.md`**: Comprehensive PL/SQL documentation
- **`FinGuard_Complete_PL_SQL.sql`**: Complete PL/SQL implementation

### **Key Documentation Sections**
- **📊 Database Schema**: Complete 14-table schema documentation
- **🔗 Blockchain Implementation**: SHA-256 blockchain with fraud detection
- **🔧 Stored Procedures**: 8 optimized procedures for core operations
- **📈 Functions**: 4 analytical functions for risk assessment
- **🔔 Triggers**: 4 audit triggers for automatic logging
- **🛡️ Security Features**: Role-based access, fraud detection, audit trails
- **📋 Query Reference**: Common database queries used in application
