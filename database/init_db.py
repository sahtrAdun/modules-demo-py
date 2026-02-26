import sqlite3
import os

def create_database():
    db_path = 'shoe_store.db'
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    schema_path = os.path.join('database', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    conn.commit()
    conn.close()
    
    print("База данных успешно создана")
    return True

if __name__ == "__main__":
    create_database()