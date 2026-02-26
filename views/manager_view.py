from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3
import os
from views.product_list import ProductListWindow
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QLabel
from PyQt5.QtGui import QPixmap, QColor

class ManagerView(ProductListWindow):
    def __init__(self, main_app):
        self.original_products = []
        self.current_sort = None
        self.current_filter = None
        self.current_search = ""
        super().__init__(main_app)
        self.setWindowTitle("ООО Обувь - Менеджер")
        
    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: 'Times New Roman';
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #7FFF00;
                border-radius: 4px;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton {
                background-color: #7FFF00;
                color: black;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00FA9A;
            }
            QPushButton.orders {
                background-color: #00FA9A;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        pixmap = QPixmap('assets/logo.png')
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        header_layout.addWidget(logo_label)
        
        title = QLabel("Панель менеджера")
        title.setFont(QFont('Times New Roman', 20, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        user_info = QLabel(f"Пользователь: {self.main_app.current_user['name']}")
        user_info.setFont(QFont('Times New Roman', 12))
        header_layout.addWidget(user_info)
        
        logout_btn = QPushButton("Выход")
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        
        main_layout.addLayout(header_layout)
        
        controls_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск товаров...")
        self.search_input.textChanged.connect(self.apply_filters)
        controls_layout.addWidget(self.search_input)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Без сортировки", "По количеству (возрастание)", "По количеству (убывание)"])
        self.sort_combo.currentTextChanged.connect(self.apply_filters)
        controls_layout.addWidget(self.sort_combo)
        
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("Все поставщики")
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT supplier_name FROM Suppliers ORDER BY supplier_name")
            suppliers = cursor.fetchall()
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier[0])
            conn.close()
        except:
            pass
        
        self.supplier_combo.currentTextChanged.connect(self.apply_filters)
        controls_layout.addWidget(self.supplier_combo)
        
        orders_btn = QPushButton("Заказы")
        orders_btn.setProperty("class", "orders")
        orders_btn.clicked.connect(self.open_orders)
        controls_layout.addWidget(orders_btn)
        
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "Фото", "Артикул", "Наименование", "Категория", "Описание", 
            "Производитель", "Поставщик", "Цена", "Ед. изм.",
            "Количество", "Скидка", "Итоговая цена"
        ])
        
        header = self.table.horizontalHeader()
        for i in range(12):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
        
        self.load_original_products()
    
    def load_original_products(self):
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.product_id, p.article, p.product_name, c.category_name, p.description,
                       m.manufacturer_name, s.supplier_name, p.price, u.unit_name,
                       p.quantity, p.discount, 
                       ROUND(p.price * (100 - p.discount) / 100, 2) as final_price,
                       p.image_path
                FROM Products p
                JOIN Categories c ON p.category_id = c.category_id
                JOIN Manufacturers m ON p.manufacturer_id = m.manufacturer_id
                JOIN Suppliers s ON p.supplier_id = s.supplier_id
                JOIN Units u ON p.unit_id = u.unit_id
                ORDER BY p.product_id
            """)
            self.original_products = cursor.fetchall()
            conn.close()
            print(f"Загружено товаров: {len(self.original_products)}")
            self.display_products(self.original_products)
        except Exception as e:
            print(f"Ошибка загрузки товаров: {e}")
            import traceback
            traceback.print_exc()
    
    def apply_filters(self):
        filtered_products = self.original_products.copy()
        
        search_text = self.search_input.text().lower()
        if search_text:
            filtered_products = [p for p in filtered_products if 
                               search_text in str(p[1]).lower() or  # article
                               search_text in str(p[2]).lower() or  # name
                               search_text in str(p[3]).lower() or  # category
                               search_text in str(p[4] or "").lower() or  # description
                               search_text in str(p[5]).lower() or  # manufacturer
                               search_text in str(p[6]).lower()]    # supplier
        
        selected_supplier = self.supplier_combo.currentText()
        if selected_supplier != "Все поставщики":
            filtered_products = [p for p in filtered_products if p[6] == selected_supplier]
        
        sort_option = self.sort_combo.currentText()
        if sort_option == "По количеству (возрастание)":
            filtered_products.sort(key=lambda x: x[9])
        elif sort_option == "По количеству (убывание)":
            filtered_products.sort(key=lambda x: x[9], reverse=True)
        
        self.display_products(filtered_products)
    
    def display_products(self, products):
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            product_id, article, name, category, desc, manufacturer, supplier, price, unit, quantity, discount, final_price, image_path = product
            
            image_label = QLabel()
            if image_path and os.path.exists(os.path.join('product_images', image_path)):
                pixmap = QPixmap(os.path.join('product_images', image_path))
            elif image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
            else:
                pixmap = QPixmap('assets/picture.png')
            
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 0, image_label)
            
            self.table.setItem(row, 1, QTableWidgetItem(article))
            self.table.setItem(row, 2, QTableWidgetItem(name))
            self.table.setItem(row, 3, QTableWidgetItem(category))
            self.table.setItem(row, 4, QTableWidgetItem(desc[:50] + "..." if desc and len(desc) > 50 else desc))
            self.table.setItem(row, 5, QTableWidgetItem(manufacturer))
            self.table.setItem(row, 6, QTableWidgetItem(supplier))
            self.table.setItem(row, 7, QTableWidgetItem(f"{price:.2f}"))
            self.table.setItem(row, 8, QTableWidgetItem(unit))
            self.table.setItem(row, 9, QTableWidgetItem(str(quantity)))
            self.table.setItem(row, 10, QTableWidgetItem(f"{discount}%"))
            
            if discount > 0:
                price_item = QTableWidgetItem(f"{price:.2f}")
                price_item.setForeground(QColor(255, 0, 0))
                font = price_item.font()
                font.setStrikeOut(True)
                price_item.setFont(font)
                
                final_price_item = QTableWidgetItem(f"{final_price:.2f}")
                final_price_item.setForeground(QColor(0, 0, 0))
                
                self.table.setItem(row, 11, final_price_item)
            else:
                self.table.setItem(row, 11, QTableWidgetItem(f"{price:.2f}"))
            
            if discount > 15:
                for col in range(12):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(46, 139, 87))
            
            if quantity == 0:
                for col in range(12):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(173, 216, 230))
    
    def open_orders(self):
        from views.orders_view import OrdersView
        self.main_app.stacked_widget.addWidget(OrdersView(self.main_app))
        self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.count() - 1)