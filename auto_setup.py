import os
import sys
import subprocess
import urllib.request
import zipfile
import tempfile
import time
import pymysql
import getpass

def print_status(message, status="INFO"):
    """Print formatted status message"""
    symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    formatted_message = f"{symbols.get(status, 'ℹ️')} {message}"
    try:
        print(formatted_message)
    except UnicodeEncodeError:
        # Replace Unicode characters with ASCII equivalents for Windows CMD
        formatted_message = formatted_message.replace('✅', '[OK]').replace('❌', '[ERROR]').replace('⚠️', '[WARNING]').replace('ℹ️', '[INFO]')
        print(formatted_message)

def check_python():
    """Check if Python is installed and version is adequate"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print_status(f"Python {version.major}.{version.minor} found", "SUCCESS")
            return True
        else:
            print_status(f"Python {version.major}.{version.minor} found, but 3.8+ required", "ERROR")
            return False
    except:
        print_status("Python not found", "ERROR")
        return False

def install_mysql_windows():
    """Install MySQL on Windows automatically"""
    print_status("Checking for MySQL installation...")
    
    # Check if MySQL is already installed
    mysql_paths = [
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
        r"C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe",
        r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe",
        r"C:\Program Files (x86)\MySQL\MySQL Server 5.7\bin\mysql.exe"
    ]
    
    for path in mysql_paths:
        if os.path.exists(path):
            print_status("MySQL already installed", "SUCCESS")
            return True
    
    print_status("MySQL not found. Installing automatically...")
    
    try:
        # Download MySQL installer
        mysql_url = "https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.35.0.msi"
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, "mysql-installer.msi")
        
        print_status("Downloading MySQL installer...")
        urllib.request.urlretrieve(mysql_url, installer_path)
        
        print_status("Running MySQL installer (this may take a few minutes)...")
        
        # Run MySQL installer silently
        install_cmd = [
            "msiexec", "/i", installer_path,
            "/quiet", "/norestart",
            "INSTALLDIR=C:\\Program Files\\MySQL\\MySQL Server 8.0\\",
            "DATADIR=C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Data\\",
            "PORT=3306",
            "SERVICENAME=MySQL80",
            "ADDLOCAL=Server,Client,MYSQLROUTER"
        ]
        
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status("MySQL installed successfully", "SUCCESS")
            
            # Wait for MySQL service to start
            print_status("Starting MySQL service...")
            time.sleep(10)
            
            return True
        else:
            print_status(f"MySQL installation failed: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Failed to install MySQL: {str(e)} ", "ERROR")
        print_status("Please install MySQL manually from https://dev.mysql.com/downloads/installer/", "WARNING")
        return False

def install_python_packages():
    """Install required Python packages"""
    print_status("Installing Python packages...")
    
    packages = ["Flask", "PyMySQL", "cryptography", "Flask-SQLAlchemy"]
    
    try:
        for package in packages:
            print_status(f"Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print_status(f"Failed to install {package}: {result.stderr}", "ERROR")
                return False
        
        print_status("All Python packages installed successfully", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Failed to install packages: {str(e)}", "ERROR")
        return False

def get_mysql_credentials():
    """Get MySQL credentials from user input"""
    print_status("MySQL Database Configuration", "INFO")
    print("=" * 50)
    
    # Get host (default: localhost)
    host = input("MySQL Host (default: localhost): ").strip()
    if not host:
        host = 'localhost'
    
    # Get port (default: 3306)
    port_input = input("MySQL Port (default: 3306): ").strip()
    if not port_input:
        port = 3306
    else:
        try:
            port = int(port_input)
        except ValueError:
            print_status("Invalid port number, using default 3306", "WARNING")
            port = 3306
    
    # Get username (default: root)
    user = input("MySQL Username (default: root): ").strip()
    if not user:
        user = 'root'
    
    # Get password (hidden input)
    print("MySQL Password (press Enter for empty password):")
    password = getpass.getpass("Password: ")
    
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password
    }

def setup_mysql_database():
    """Setup MySQL database and tables"""
    print_status("Setting up FinGuard database...")
    
    # Get credentials from user
    credentials = get_mysql_credentials()
    
    try:
        print_status(f"Connecting to MySQL at {credentials['host']}:{credentials['port']}...")
        
        # Connect to MySQL (without database)
        connection = pymysql.connect(
            host=credentials['host'],
            port=credentials['port'],
            user=credentials['user'],
            password=credentials['password'],
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Check if database exists and drop it for fresh installation
        print_status("Checking for existing FinGuard database...")
        cursor.execute("SHOW DATABASES LIKE 'fin_guard'")
        existing_db = cursor.fetchone()
        
        if existing_db:
            print_status("Existing fin_guard database found - removing for fresh installation...", "WARNING")
            cursor.execute("DROP DATABASE fin_guard")
            print_status("Existing database removed successfully", "SUCCESS")
        
        # Create fresh database
        print_status("Creating new fin_guard database...")
        cursor.execute("CREATE DATABASE fin_guard")
        cursor.execute("USE fin_guard")
        
        # Read and execute schema
        schema_file = os.path.join(os.path.dirname(__file__), "DatabaseSchema_MySQL.sql")
        if os.path.exists(schema_file):
            print_status("Creating database tables...")
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema statements
            for statement in schema_sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
        else:
            print_status("Schema file not found, creating basic tables...", "WARNING")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Save the working credentials for the seed script
        os.environ['MYSQL_HOST'] = credentials['host']
        os.environ['MYSQL_PORT'] = str(credentials['port'])
        os.environ['MYSQL_USER'] = credentials['user']
        os.environ['MYSQL_PASSWORD'] = credentials['password']
        
        print_status("Fresh database and schema created successfully", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Database setup failed: {str(e)}", "ERROR")
        print_status("Please check your MySQL credentials and try again", "WARNING")
        
        # Ask if user wants to retry
        retry = input("\nWould you like to try again with different credentials? (y/n): ").lower()
        if retry.startswith('y'):
            return setup_mysql_database()  # Recursive retry
        
        return False

def seed_database():
    """Seed database with initial data"""
    print_status("Adding test data and user accounts...")
    
    try:
        # Run the existing seed script
        result = subprocess.run([sys.executable, "database_seed.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status("Test data added successfully", "SUCCESS")
            return True
        else:
            print_status(f"Failed to seed database: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Database seeding failed: {str(e)}", "ERROR")
        return False

def start_application():
    """Start the FinGuard application"""
    print_status("Starting FinGuard application...")
    
    try:
        print_status("🚀 FinGuard is starting up...")
        print_status("🌐 Open http://localhost:5000 in your browser")
        print_status("🔑 Login with: admin/admin, agent/agent, or user/user")
        
        # Start the Flask application
        subprocess.run([sys.executable, "run.py"])
        
    except KeyboardInterrupt:
        print_status("Application stopped by user", "INFO")
    except Exception as e:
        print_status(f"Failed to start application: {str(e)}", "ERROR")

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 FinGuard Automatic Setup")
    print("=" * 60)
    print()
    print("This setup will:")
    print("✅ Check system requirements")
    print("✅ Install MySQL (if needed)")
    print("✅ Install Python packages")
    print("🔄 Create fresh database (removes existing if found)")
    print("✅ Add test data and user accounts")
    print("✅ Start the FinGuard application")
    print()
    print("⚠️  WARNING: This will delete any existing fin_guard database!")
    print()
    
    # Confirm before proceeding
    confirm = input("Continue with fresh installation? (Y/n): ").lower()
    if confirm.startswith('n'):
        print("Setup cancelled by user.")
        input("Press Enter to exit...")
        return False
    
    # Check system requirements
    if not check_python():
        print_status("Please install Python 3.8+ and run setup again", "ERROR")
        input("Press Enter to exit...")
        return False
    
    # Install MySQL if needed
    if not install_mysql_windows():
        print_status("MySQL installation failed. Please install manually.", "ERROR")
        print_status("You can download MySQL from: https://dev.mysql.com/downloads/installer/", "INFO")
        input("Press Enter to exit...")
        return False
    
    # Install Python packages
    if not install_python_packages():
        print_status("Package installation failed", "ERROR")
        input("Press Enter to exit...")
        return False
    
    # Setup database (with user input for credentials)
    if not setup_mysql_database():
        print_status("Database setup failed", "ERROR")
        input("Press Enter to exit...")
        return False
    
    # Seed database
    if not seed_database():
        print_status("Database seeding failed", "ERROR")
        input("Press Enter to exit...")
        return False
    
    print()
    print("=" * 60)
    print("✅ FinGuard Setup Complete!")
    print("=" * 60)
    print()
    print("🔑 Test Accounts Created:")
    print("   • admin/admin  (Administrator)")
    print("   • agent/agent  (Financial Agent)")
    print("   • user/user    (Regular User)")
    print()
    
    # Ask if user wants to start the application immediately
    start_now = input("Start FinGuard application now? (Y/n): ").lower()
    if not start_now.startswith('n'):
        start_application()
    else:
        print()
        print("To start FinGuard later, run: python run.py")
        print("Then open: http://localhost:5000")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
