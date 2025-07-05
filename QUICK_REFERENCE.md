# FinGuard - Quick Reference

## 🚀 **Setup (2 steps)**
1. **Install MySQL** (if not already installed)
2. **Run**: `migrate_to_mysql.bat`

## 🔑 **Test Accounts**
| Username | Password | What you can do |
|----------|----------|-----------------|
| admin    | admin    | Manage users, view all data |
| agent    | agent    | Add/remove money for users |
| user     | user     | Send money, create budgets |

## 🌐 **Start App**
```
python run.py
```
Open: http://localhost:5000

## 💡 **Key Features to Try**
- **Dashboard**: View balance, transactions, charts
- **Send Money**: Transfer funds between users
- **Budget**: Create and manage budgets
- **Profile**: Update personal information
- **Admin Panel**: (admin only) Manage users
- **Agent Panel**: (agent only) Add money for users

## 🆘 **Common Issues**
- **MySQL error**: Make sure MySQL is installed and running
- **Permission denied**: Run as administrator
- **Can't login**: Use the test accounts above
- **Page error**: Restart with `python run.py`

## 📁 **Important Files**
- `migrate_to_mysql.bat` - Setup script
- `run.py` - Start the application
- `SETUP_GUIDE.md` - Detailed setup instructions

---
**That's it! Everything else is automatic.** 🎉
