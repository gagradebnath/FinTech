# FinGuard: Personal Finance Management Web App

> **🚀 Want to try it now? Just run `migrate_to_mysql.bat` → `python run.py` → Open http://localhost:5000**  
> Login: admin/admin, agent/agent, or user/user

FinGuard is a comprehensive personal finance management web application with modern UI, role-based access control, budget planning, and transaction management.

## 🚀 **2-Step Setup**

1. **Install MySQL** (if not already installed)
2. **Run setup**: `migrate_to_mysql.bat`

That's it! The script handles everything else automatically.

## 💻 **Requirements**

- Windows with MySQL installed
- Python 3.8+
- Internet connection (for package installation)

## � **Test It Instantly**

After setup, login with these accounts:

| Username | Password | Role  |
|----------|----------|-------|
| admin    | admin    | Admin |
| agent    | agent    | Agent |
| user     | user     | User  |

Start the app: `python run.py` → Open http://localhost:5000

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

## Project Structure

```text
app/
    __init__.py             # App factory, DB connection, JSON encoder
    config.py               # Flask configuration
    models.py               # (placeholder)
    README.md               # App module documentation
    routes/
        __init__.py         # Blueprint registration
        user.py             # User authentication and dashboard routes
        admin.py            # Admin dashboard and management routes
        agent.py            # Agent dashboard and operations routes
        budget.py           # Budget planning and saving routes
        transaction.py      # Money transfer routes
        fraud.py            # Fraud reporting routes
        chat.py             # AI chat routes (placeholder)
        README.md           # Routes documentation
    static/
        README.md           # Static assets documentation
        assets/             # Images and other assets
        css/
            style.css       # Main stylesheet
## 📁 **Project Structure**

```
FinGuard/
├── migrate_to_mysql.bat    # 🚀 Setup script (run this!)
├── run.py                  # Start the application
├── app/                    # Main application code
│   ├── routes/            # Web pages and API endpoints
│   ├── templates/         # HTML templates
│   ├── static/           # CSS, JavaScript, images
│   └── utils/            # Business logic and database operations
└── docs/                  # Setup guides and documentation
```

## 🆘 **Need Help?**

### **Setup Issues**
- **MySQL not found**: Install MySQL from https://dev.mysql.com/downloads/
- **Permission denied**: Run as administrator or check MySQL user permissions
- **Connection failed**: Verify MySQL service is running

### **Application Issues**  
- **Can't login**: Use test accounts (admin/admin, agent/agent, user/user)
- **Page errors**: Restart the app with `python run.py`
- **Missing data**: Rerun setup script to recreate sample data

### **Get More Help**
- 📖 Detailed setup: `SETUP_GUIDE.md`
- 🔧 Configuration: `CREDENTIAL_SETUP.md`  
- 📋 Full documentation: Other `.md` files in the project
MIGRATION_GUIDE.md          # Detailed migration guide ✅
FINAL_MIGRATION_STATUS.md   # Complete migration status ✅
TRANSACTION_TYPE_FIX.md     # Transaction ENUM fix details ✅
README.md                   # This file
```

## 🚀 Setup & Usage (MySQL)

**Quick Setup:**
```cmd
migrate_to_mysql.bat
```

**Manual Setup:**
1. **Install dependencies:**
   ```cmd
   pip install PyMySQL cryptography Flask-SQLAlchemy
   ```
2. **Initialize MySQL database:**
   ```cmd
   python seed_mysql.py
   ```
3. **Run the app:**
   ```cmd
   python run.py
   ```
4. **Access the app:**
   Open [http://localhost:5000](http://localhost:5000)

## 🔑 Demo Accounts

After running the setup, login with these test accounts:

| Role   | Username | Password | Features |
|--------|----------|----------|----------|
| Admin  | admin    | admin    | User management, admin dashboard |
| Agent  | agent    | agent    | Add money, cash out, agent dashboard |
| User   | user     | user     | Send money, budgets, profile |

All accounts start with 10,000 balance for testing.

## 💾 Database (MySQL)

- **Database**: MySQL 8.0+ (`fin_guard` database)
- **Schema**: `DatabaseSchema_MySQL.sql` with proper ENUM constraints
- **Setup Script**: `seed_mysql.py` (automated database creation)
- **Connection**: PyMySQL with robust error handling
- **Features**: 
  - ✅ Foreign key relationships
  - ✅ ENUM constraints for data integrity
## 🏗️ **Built With**

- **Python Flask** - Web framework
- **MySQL** - Database  
- **Bootstrap 5** - Modern UI
- **Chart.js** - Data visualization

## 💡 **What Makes It Special**

✅ **Fully Working**: All features tested and functional  
✅ **Easy Setup**: One script does everything  
✅ **Modern Design**: Dark theme, responsive layout  
✅ **Real-World Ready**: Role permissions, security features  
✅ **No Config Hassle**: Automatic database setup  

---

**Ready to explore personal finance management? Run `migrate_to_mysql.bat` and start in under 5 minutes!**
- **Edit Python code:**
  - All backend logic is in the `app/routes/` directory. For example, to change budget logic, edit `budget.py`.
## 🚀 **Alternative Manual Setup**

If you prefer manual control:

```cmd
pip install PyMySQL cryptography Flask-SQLAlchemy
python seed_mysql.py
python run.py
```

Open http://localhost:5000 when ready!

## 🏗️ **Built With**

- **Python Flask** - Web framework
- **MySQL** - Database  
- **Bootstrap 5** - Modern UI
- **Chart.js** - Data visualization

## 💡 **What Makes It Special**

✅ **Fully Working**: All features tested and functional  
✅ **Easy Setup**: One script does everything  
✅ **Modern Design**: Dark theme, responsive layout  
✅ **Real-World Ready**: Role permissions, security features  
✅ **No Config Hassle**: Automatic database setup  

---

**Ready to explore personal finance management? Run `migrate_to_mysql.bat` and start in under 5 minutes!**
