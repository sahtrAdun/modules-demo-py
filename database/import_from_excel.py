import sqlite3
import pandas as pd
import os
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox

class ExcelImporter:
    def __init__(self, db_path='shoe_store.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        self.conn.close()
    
    def clear_tables(self):
        """Очистка таблиц в правильном порядке"""
        tables = ['OrderItems', 'Orders', 'Products', 'Users', 'Suppliers', 
                  'Categories', 'Manufacturers', 'Units', 'PickupPoints']
        for table in tables:
            try:
                self.cursor.execute(f"DELETE FROM {table}")
            except:
                pass
        try:
            self.cursor.execute("DELETE FROM sqlite_sequence")
        except:
            pass
        self.conn.commit()
        print("Таблицы очищены")
    
    def import_pickup_points(self, file_path):
        """Импорт пунктов выдачи из pick_points.xlsx"""
        try:
            df = pd.read_excel(file_path, header=None, names=['address'])
            
            count = 0
            for _, row in df.iterrows():
                address = str(row['address']).strip()
                if address and address != 'nan':
                    try:
                        self.cursor.execute(
                            "INSERT INTO PickupPoints (address) VALUES (?)",
                            (address,)
                        )
                        count += 1
                    except sqlite3.IntegrityError:
                        pass
            
            self.conn.commit()
            print(f"Импортировано пунктов выдачи: {count}")
            return True
        except Exception as e:
            print(f"Ошибка импорта пунктов выдачи: {e}")
            return False
    
    def import_products(self, file_path):
        """Импорт товаров из products.xlsx"""
        try:
            df = pd.read_excel(file_path)
            
            units = df['Единица измерения'].dropna().unique()
            for unit in units:
                unit = str(unit).strip()
                try:
                    self.cursor.execute(
                        "INSERT INTO Units (unit_name) VALUES (?)",
                        (unit,)
                    )
                except sqlite3.IntegrityError:
                    pass
            
            suppliers = df['Поставщик'].dropna().unique()
            for supplier in suppliers:
                supplier = str(supplier).strip()
                try:
                    self.cursor.execute(
                        "INSERT INTO Suppliers (supplier_name) VALUES (?)",
                        (supplier,)
                    )
                except sqlite3.IntegrityError:
                    pass
            
            manufacturers = df['Производитель'].dropna().unique()
            for manufacturer in manufacturers:
                manufacturer = str(manufacturer).strip()
                try:
                    self.cursor.execute(
                        "INSERT INTO Manufacturers (manufacturer_name) VALUES (?)",
                        (manufacturer,)
                    )
                except sqlite3.IntegrityError:
                    pass
            
            categories = df['Категория товара'].dropna().unique()
            for category in categories:
                category = str(category).strip()
                try:
                    self.cursor.execute(
                        "INSERT INTO Categories (category_name) VALUES (?)",
                        (category,)
                    )
                except sqlite3.IntegrityError:
                    pass
            
            self.conn.commit()
            
            self.cursor.execute("SELECT unit_id, unit_name FROM Units")
            unit_map = {name: id for id, name in self.cursor.fetchall()}
            
            self.cursor.execute("SELECT supplier_id, supplier_name FROM Suppliers")
            supplier_map = {name: id for id, name in self.cursor.fetchall()}
            
            self.cursor.execute("SELECT manufacturer_id, manufacturer_name FROM Manufacturers")
            manufacturer_map = {name: id for id, name in self.cursor.fetchall()}
            
            self.cursor.execute("SELECT category_id, category_name FROM Categories")
            category_map = {name: id for id, name in self.cursor.fetchall()}
            
            products_count = 0
            for _, row in df.iterrows():
                try:
                    article = str(row['Артикул']).strip()
                    name = str(row['Наименование товара']).strip()
                    unit = str(row['Единица измерения']).strip()
                    price = float(row['Цена'])
                    supplier = str(row['Поставщик']).strip()
                    manufacturer = str(row['Производитель']).strip()
                    category = str(row['Категория товара']).strip()
                    discount = int(row['Действующая скидка']) if pd.notna(row['Действующая скидка']) else 0
                    quantity = int(row['Кол-во на складе']) if pd.notna(row['Кол-во на складе']) else 0
                    description = str(row['Описание товара']).strip() if pd.notna(row['Описание товара']) else None
                    photo = str(row['Фото']).strip() if pd.notna(row['Фото']) else None
                    
                    self.cursor.execute("""
                        INSERT INTO Products 
                        (article, product_name, unit_id, price, supplier_id, manufacturer_id, 
                         category_id, discount, quantity, description, image_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article, name, unit_map[unit], price,
                        supplier_map[supplier], manufacturer_map[manufacturer],
                        category_map[category], discount, quantity, description, photo
                    ))
                    products_count += 1
                    
                except Exception as e:
                    print(f"Ошибка импорта товара {row.get('Артикул', 'unknown')}: {e}")
            
            self.conn.commit()
            print(f"Импортировано товаров: {products_count}")
            return True
            
        except Exception as e:
            print(f"Ошибка импорта товаров: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def import_users(self, file_path):
        """Импорт пользователей из users.xlsx"""
        try:
            df = pd.read_excel(file_path)
            
            role_map = {
                'Администратор': 'admin',
                'Менеджер': 'manager',
                'Авторизированный клиент': 'client'
            }
            
            users_count = 0
            for _, row in df.iterrows():
                try:
                    role_ru = str(row['Роль сотрудника']).strip()
                    role = role_map.get(role_ru, 'client')
                    full_name = str(row['ФИО']).strip()
                    login = str(row['Логин']).strip()
                    password = str(row['Пароль']).strip()
                    
                    self.cursor.execute("""
                        INSERT INTO Users (full_name, login, password, role)
                        VALUES (?, ?, ?, ?)
                    """, (full_name, login, password, role))
                    users_count += 1
                    
                except sqlite3.IntegrityError:
                    print(f"Пользователь {login} уже существует")
                except Exception as e:
                    print(f"Ошибка импорта пользователя: {e}")
            
            self.conn.commit()
            print(f"Импортировано пользователей: {users_count}")
            
            self.cursor.execute("SELECT user_id, full_name FROM Users")
            self.user_map = {name: id for id, name in self.cursor.fetchall()}
            return True
            
        except Exception as e:
            print(f"Ошибка импорта пользователей: {e}")
            return False
    
    def import_orders(self, file_path):
        """Импорт заказов из orders.xlsx"""
        try:
            df = pd.read_excel(file_path)
            
            self.cursor.execute("SELECT pickup_point_id, address FROM PickupPoints")
            pickup_points = self.cursor.fetchall()
            
            status_map = {
                'Завершен': 'completed',
                'Новый': 'new',
                'В обработке': 'processing',
                'Отменен': 'cancelled'
            }
            
            orders_count = 0
            for _, row in df.iterrows():
                try:
                    order_id = int(row['Номер заказа'])
                    order_article = str(row['Артикул заказа']).strip()
                    
                    order_date = row['Дата заказа']
                    if pd.isna(order_date):
                        order_date = None
                    elif isinstance(order_date, datetime):
                        order_date = order_date.strftime('%Y-%m-%d')
                    else:
                        try:
                            order_date = pd.to_datetime(order_date).strftime('%Y-%m-%d')
                        except:
                            order_date = str(order_date).split()[0] if ' ' in str(order_date) else str(order_date)
                    
                    issue_date = row['Дата доставки']
                    if pd.isna(issue_date):
                        issue_date = None
                    elif isinstance(issue_date, datetime):
                        issue_date = issue_date.strftime('%Y-%m-%d')
                    else:
                        try:
                            issue_date = pd.to_datetime(issue_date).strftime('%Y-%m-%d')
                        except:
                            issue_date = str(issue_date).split()[0] if ' ' in str(issue_date) else str(issue_date)
                    
                    pickup_number = int(str(row['Адрес пункта выдачи']).strip())
                    if pickup_number <= len(pickup_points):
                        pickup_point_id = pickup_points[pickup_number - 1][0]
                    else:
                        pickup_point_id = 1
                    
                    full_name = str(row['ФИО авторизированного клиента']).strip()
                    user_id = self.user_map.get(full_name, 1)
                    
                    status_ru = str(row['Статус заказа']).strip()
                    status = status_map.get(status_ru, 'new')
                    
                    self.cursor.execute("""
                        INSERT INTO Orders 
                        (order_id, order_article, user_id, status, pickup_point_id, order_date, issue_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (order_id, order_article, user_id, status, pickup_point_id, order_date, issue_date))
                    
                    orders_count += 1
                    
                except Exception as e:
                    print(f"Ошибка импорта заказа {row.get('Номер заказа', 'unknown')}: {e}")
            
            self.conn.commit()
            print(f"Импортировано заказов: {orders_count}")
            return True
            
        except Exception as e:
            print(f"Ошибка импорта заказов: {e}")
            import traceback
            traceback.print_exc()
            return False

def import_all_data():
    """Главная функция импорта всех данных"""
    db_init_dir = 'db_init'
    
    if not os.path.exists(db_init_dir):
        print(f"Папка {db_init_dir} не найдена")
        return False
    
    required_files = {
        'pick_points.xlsx': 'Пункты выдачи',
        'products.xlsx': 'Товары',
        'users.xlsx': 'Пользователи',
        'orders.xlsx': 'Заказы'
    }
    
    missing_files = []
    for filename, description in required_files.items():
        if not os.path.exists(os.path.join(db_init_dir, filename)):
            missing_files.append(f"{description} ({filename})")
    
    if missing_files:
        print("Отсутствуют файлы:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    importer = ExcelImporter()
    success = True
    
    try:
        # Очищаем таблицы
        importer.clear_tables()
        
        print("\n" + "="*50)
        print("ИМПОРТ ДАННЫХ")
        print("="*50)
        
        print("\n1. Импорт пунктов выдачи...")
        if not importer.import_pickup_points(os.path.join(db_init_dir, 'pick_points.xlsx')):
            success = False
        
        print("\n2. Импорт товаров и справочников...")
        if not importer.import_products(os.path.join(db_init_dir, 'products.xlsx')):
            success = False
        
        print("\n3. Импорт пользователей...")
        if not importer.import_users(os.path.join(db_init_dir, 'users.xlsx')):
            success = False
        
        print("\n4. Импорт заказов...")
        if not importer.import_orders(os.path.join(db_init_dir, 'orders.xlsx')):
            success = False
        
        importer.conn.commit()
        
        print("\n" + "="*50)
        print("ИТОГИ ИМПОРТА")
        print("="*50)
        
        tables = ['PickupPoints', 'Units', 'Suppliers', 'Manufacturers', 
                  'Categories', 'Products', 'Users', 'Orders']
        
        for table in tables:
            try:
                count = importer.cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                print(f"{table}: {count} записей")
            except:
                print(f"{table}: ошибка получения данных")
        
        if success:
            print("\nИМПОРТ УСПЕШНО ЗАВЕРШЕН!")
        else:
            print("\nИМПОРТ ЗАВЕРШЕН С ОШИБКАМИ")
        
        return success
        
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        importer.close()

if __name__ == "__main__":
    import_all_data()