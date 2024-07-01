import pyodbc
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_migrate import Migrate


# Initialize Flask app
app = Flask(__name__)

# Replace placeholders with your actual details
server = 'PCFSALAH-20KBX\\SQLEXPRESS01'  # Escape backslashes properly
port = '1433'  # Change if needed
database_name = 'TV_Display'
username = 'SALAH'
password = 'slhdouas2002'

# Specify the ODBC driver name
driver = 'ODBC Driver 17 for SQL Server'

# Connect to the master database (used for database creation)
conn_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;UID={username};PWD={password}"
with pyodbc.connect(conn_string, autocommit=True) as conn:  # Set autocommit to True
    with conn.cursor() as cursor:
        # Check if the database exists
        cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name = '{database_name}'")
        if cursor.fetchone()[0] == 0:
            # Create database using T-SQL statement
            sql = f"CREATE DATABASE {database_name}"
            cursor.execute(sql)
            print(f"Database '{database_name}' created successfully!")

# Define your SQL Server database URI
sql_server_uri = f"mssql+pyodbc://{username}:{password}@{server}/{database_name}?driver={driver}"

# Link the Flask app to the SQL Server database
app.config['SQLALCHEMY_DATABASE_URI'] = sql_server_uri

# Enable modification tracking
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'

# Initialize SQLAlchemy
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'

# Import models to register them with the SQLAlchemy instance
from TV_Display import models
migrate = Migrate(app, db)

# Create all database tables
with app.app_context():
    db.create_all()

# Import routes to register them with the app
from TV_Display import routes


app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)




