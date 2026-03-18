import sqlite3
import os

db_path = 'data/matches.db'
print(f"Checking database at {db_path}...")

if not os.path.exists(db_path):
    print("Database file NOT FOUND!")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables found: {tables}")
        
        if 'preferences' in tables:
            print("Table 'preferences' exists.")
        else:
            print("Table 'preferences' is MISSING!")
            
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")
