# FinGuard: Personal Finance Management Web App

> **🚀 INSTANT SETUP: Just run `setup.bat` → Open http://localhost:5000**  
> Login: admin/admin, agent/agent, or user/user

FinGuard is a comprehensive personal finance management web application with modern UI, role-based access control, budget planning, and transaction management.

## 🚀 **ONE-CLICK SETUP**

**Just double-click:** `setup.bat`

The setup will prompt you for MySQL credentials, then everything happens automatically:
- ✅ Installs MySQL (if needed)
- ✅ Installs Python packages  
- 🔄 Creates fresh database (removes existing if found)
- ✅ Adds test data and user accounts
- ✅ Starts the application

⚠️ **Note**: This will delete any existing `fin_guard` database for a clean installation.

## 💻 **Requirements**

- Windows OS
- Python 3.8+ (will be installed if missing)
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

- **💼 Multi-Role System**: Admin, Agent, User dashboards
- **💰 Financial Management**: Budgets, expenses, money transfers
- **📊 Modern UI**: Dark theme, responsive design, charts
- **🔒 Security**: Role-based permissions, fraud reporting
- **📱 User-Friendly**: Easy registration, profile management

## 🛠️ **What's Inside**

- **Send Money**: Transfer funds between users
- **Budget Planning**: Create and manage budgets
- **Transaction History**: View all financial activities  
- **Admin Panel**: User management and monitoring
- **Agent Tools**: Add money, cash out operations
- **Profile Management**: Update personal information

## 📁 **Project Structure**

```
FinGuard/
├── setup.bat              # 🚀 One-click setup script (run this!)
├── auto_setup.py          # Automatic MySQL installation and setup
├── database_seed.py       # Database seeding with test data
├── run.py                 # Start the application
├── app/                   # Main application code
│   ├── routes/           # Web pages and API endpoints
│   ├── templates/        # HTML templates
│   ├── static/          # CSS, JavaScript, images
│   └── utils/           # Business logic and database operations
└── DatabaseSchema_MySQL.sql  # MySQL database schema
```

## 🆘 **Need Help?**

### **Setup Issues**
- **MySQL installation fails**: The script will prompt to install manually from https://dev.mysql.com/downloads/
- **Permission denied**: Run `setup.bat` as administrator
- **Python not found**: Install Python 3.8+ from https://python.org
- **MySQL connection fails**: Double-check your MySQL credentials (host, port, username, password)

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
