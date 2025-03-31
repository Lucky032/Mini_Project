import pyodbc
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=AJAY\SQLEXPRESS;'  # Replace with your SQL Server instance name
            'DATABASE=sports;'  # Replace with your database name
            'Trusted_Connection=yes;'  # This enables Windows Authentication
        )
        logger.info("Database connection successful.")
        return conn
    except pyodbc.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise
