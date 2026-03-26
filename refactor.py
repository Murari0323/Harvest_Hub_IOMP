import os
import re

filepath = r'c:\Users\murar\Documents\antiG\app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace connection pool logic
old_pool = '''# Create a connection pool for better reliability
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="harvesthub_pool",
        pool_size=5,
        pool_reset_session=True,
        **db_config
    )
except mysql.connector.Error as e:
    print(f"[WARNING] Could not create connection pool at startup: {e}")
    connection_pool = None


def get_db():
    """Get a database connection from the pool (or create a fresh one)."""
    try:
        if connection_pool:
            return connection_pool.get_connection()
    except mysql.connector.Error:
        pass
    # Fallback: create a standalone connection
    return mysql.connector.connect(**db_config)'''

new_pool = '''import logging
import time

logger = logging.getLogger(__name__)

def get_db_connection(retries=3, delay=2):
    """Create and return a fresh database connection per request with retries."""
    attempt = 0
    while attempt < retries:
        try:
            conn = mysql.connector.connect(**db_config)
            if conn.is_connected():
                return conn
        except mysql.connector.Error as err:
            logger.error(f"[DB Error] Connection failed (Attempt {attempt + 1}/{retries}): {err}")
            attempt += 1
            time.sleep(delay)
    
    logger.critical("[DB Error] All retries to connect to the database failed.")
    raise mysql.connector.Error("Database connection failed after retries.")'''

content = content.replace(old_pool, new_pool)
content = content.replace('from mysql.connector import pooling\n', '')

# Replace conn = get_db()
content = content.replace('conn = get_db()', 'conn = get_db_connection()')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Replaced connection pool with get_db_connection()")
