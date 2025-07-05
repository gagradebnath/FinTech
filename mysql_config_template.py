# FinGuard MySQL Configuration Template
# Copy this file to 'mysql_config.py' and update with your credentials
# This file will be used if environment variables are not set

MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_mysql_password_here',
    'database': 'fin_guard',
    'charset': 'utf8mb4'
}

# Instructions:
# 1. Copy this file to 'mysql_config.py'
# 2. Update the password and other settings as needed
# 3. Keep 'mysql_config.py' secure and don't commit it to version control
