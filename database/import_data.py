import sqlite3
import csv
import os

def import_data():
    conn = sqlite3.connect('shoe_store.db')
    cursor = conn.cursor()
    
    data_files = {
        'users.csv': 'Users (login, password, full_name, role)',
        'categories.csv': 'Categories (category_name)',
        'manufacturers.csv': 'Manufacturers (manufacturer_name)',
        'suppliers.csv': 'Suppliers (supplier_name)',
        'units.csv': 'Units (unit_name)',
        'products.csv': 'Products (product_name, category_id, description, manufacturer_id, supplier_id, price, unit_id, quantity, discount, image_path)',
        'orders.csv': 'Orders (order_article, user_id, status, pickup_address, order_date, issue_date)',
        'order_items.csv': 'OrderItems (order_id, product_id, quantity, price_at_time)'
    }
    
    for filename, table_info in data_files.items():
        filepath = os.path.join('data', filename)
        
        if not os.path.exists(filepath):
            print(f"Файл {filename} не найден, пропускаем")
            continue
        
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            table_name = table_info.split(' ')[0]
            columns = table_info.split('(')[1].rstrip(')')
            
            placeholders = ','.join(['?' for _ in headers])
            
            for row in reader:
                try:
                    cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", row)
                except sqlite3.IntegrityError as e:
                    print(f"Ошибка при вставке в {table_name}: {e}")
    
    conn.commit()
    conn.close()
    
    print("Данные успешно импортированы")

if __name__ == "__main__":
    import_data()
