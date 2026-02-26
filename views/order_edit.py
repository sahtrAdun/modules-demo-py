from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sqlite3
import uuid

class OrderEditWindow(QWidget):
    edit_windows = []
    
    def __init__(self, main_app, order_id=None, parent_view=None):
        super().__init__()
        
        if len(OrderEditWindow.edit_windows) > 0:
            QMessageBox.warning(self, "Внимание", "Окно редактирования уже открыто")
            self.close()
            return
            
        OrderEditWindow.edit_windows.append(self)
        
        self.main_app = main_app
        self.order_id = order_id
        self.parent_view = parent_view
        self.current_items = []
        
        self.initUI()
        self.load_data()
        
    def initUI(self):
        self.setWindowTitle("ООО Обувь - " + ("Редактирование" if self.order_id else "Добавление") + " заказа")
        self.setFixedSize(800, 600)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: 'Times New Roman';
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox {
                padding: 8px;
                border: 1px solid #7FFF00;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #7FFF00;
                color: black;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00FA9A;
            }
            QPushButton.danger {
                background-color: #ff6b6b;
            }
            QPushButton.danger:hover {
                background-color: #ff5252;
            }
            QTableWidget {
                border: 1px solid #7FFF00;
                gridline-color: #7FFF00;
            }
            QHeaderView::section {
                background-color: #7FFF00;
                padding: 5px;
                border: 1px solid #00FA9A;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel(("Редактирование" if self.order_id else "Добавление") + " заказа")
        title.setFont(QFont('Times New Roman', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        
        article_layout = QHBoxLayout()
        article_layout.addWidget(QLabel("Артикул заказа:"))
        
        if self.order_id:
            self.article_label = QLabel()
            article_layout.addWidget(self.article_label)
        else:
            self.article_input = QLineEdit()
            self.article_input.setPlaceholderText("Введите артикул заказа")
            article_layout.addWidget(self.article_input)
            generate_btn = QPushButton("Сгенерировать")
            generate_btn.clicked.connect(self.generate_article)
            article_layout.addWidget(generate_btn)
        
        article_layout.addStretch()
        form_layout.addLayout(article_layout)
        
        client_layout = QHBoxLayout()
        client_layout.addWidget(QLabel("Клиент:"))
        self.client_combo = QComboBox()
        client_layout.addWidget(self.client_combo)
        client_layout.addStretch()
        form_layout.addLayout(client_layout)
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новый", "В обработке", "Выполнен", "Отменен"])
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        form_layout.addLayout(status_layout)
        
        # ИСПРАВЛЕНО: Используем pickup_combo вместо address_input
        pickup_layout = QHBoxLayout()
        pickup_layout.addWidget(QLabel("Пункт выдачи:"))
        self.pickup_combo = QComboBox()
        pickup_layout.addWidget(self.pickup_combo)
        pickup_layout.addStretch()
        form_layout.addLayout(pickup_layout)
        
        dates_layout = QHBoxLayout()
        dates_layout.addWidget(QLabel("Дата заказа:"))
        self.order_date = QDateEdit()
        self.order_date.setDate(QDate.currentDate())
        self.order_date.setCalendarPopup(True)
        dates_layout.addWidget(self.order_date)
        
        dates_layout.addWidget(QLabel("Дата выдачи:"))
        self.issue_date = QDateEdit()
        self.issue_date.setDate(QDate.currentDate())
        self.issue_date.setCalendarPopup(True)
        self.issue_date.setSpecialValueText("Не выдано")
        dates_layout.addWidget(self.issue_date)
        
        dates_layout.addStretch()
        form_layout.addLayout(dates_layout)
        
        layout.addLayout(form_layout)
        
        items_label = QLabel("Товары в заказе:")
        items_label.setFont(QFont('Times New Roman', 14, QFont.Bold))
        layout.addWidget(items_label)
        
        items_controls = QHBoxLayout()
        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(300)
        items_controls.addWidget(self.product_combo)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999)
        self.quantity_spin.setPrefix("Кол-во: ")
        items_controls.addWidget(self.quantity_spin)
        
        add_item_btn = QPushButton("Добавить товар")
        add_item_btn.clicked.connect(self.add_item)
        items_controls.addWidget(add_item_btn)
        
        items_controls.addStretch()
        layout.addLayout(items_controls)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Артикул", "Товар", "Количество", "Цена", ""])
        
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.items_table)
        
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel("Итого:"))
        self.total_label = QLabel("0.00 ₽")
        self.total_label.setFont(QFont('Times New Roman', 16, QFont.Bold))
        total_layout.addWidget(self.total_label)
        layout.addLayout(total_layout)
        
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_order)
        buttons_layout.addWidget(save_btn)
        
        if self.order_id:
            delete_btn = QPushButton("Удалить заказ")
            delete_btn.setProperty("class", "danger")
            delete_btn.clicked.connect(self.delete_order)
            buttons_layout.addWidget(delete_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        self.load_combo_data()
    
    def load_combo_data(self):
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            
            # Загружаем клиентов
            cursor.execute("SELECT user_id, full_name FROM Users WHERE role IN ('client', 'admin', 'manager') ORDER BY full_name")
            clients = cursor.fetchall()
            for user_id, name in clients:
                self.client_combo.addItem(name, user_id)
            
            # ИСПРАВЛЕНО: Загружаем пункты выдачи
            cursor.execute("SELECT pickup_point_id, address FROM PickupPoints ORDER BY address")
            points = cursor.fetchall()
            for point_id, address in points:
                self.pickup_combo.addItem(address, point_id)
            
            # Загружаем товары
            cursor.execute("""
                SELECT product_id, article, product_name, price, quantity FROM Products 
                WHERE quantity > 0 ORDER BY product_name
            """)
            products = cursor.fetchall()
            for prod_id, article, name, price, qty in products:
                self.product_combo.addItem(f"{name} ({article}) - {price} ₽ [в наличии: {qty}]", prod_id)
            
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить справочники: {str(e)}")
    
    def load_data(self):
        if not self.order_id:
            return
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT o.order_article, o.user_id, o.status, o.pickup_point_id, 
                       o.order_date, o.issue_date
                FROM Orders o
                WHERE o.order_id=?
            """, (self.order_id,))
            order = cursor.fetchone()
            
            if order:
                article, user_id, status, pickup_id, order_date, issue_date = order
                
                self.article_label.setText(article)
                
                index = self.client_combo.findData(user_id)
                if index >= 0:
                    self.client_combo.setCurrentIndex(index)
                
                status_map = {'new': 0, 'processing': 1, 'completed': 2, 'cancelled': 3}
                self.status_combo.setCurrentIndex(status_map.get(status, 0))
                
                # ИСПРАВЛЕНО: Устанавливаем пункт выдачи
                index = self.pickup_combo.findData(pickup_id)
                if index >= 0:
                    self.pickup_combo.setCurrentIndex(index)
                
                self.order_date.setDate(QDate.fromString(order_date, "yyyy-MM-dd"))
                if issue_date:
                    self.issue_date.setDate(QDate.fromString(issue_date, "yyyy-MM-dd"))
                else:
                    self.issue_date.setDate(QDate.currentDate())
                    self.issue_date.clear()
                
                # Парсим товары из строки артикула
                if article and ', ' in article:
                    parts = article.split(', ')
                    for i in range(0, len(parts), 2):
                        if i + 1 < len(parts):
                            art = parts[i]
                            qty = int(parts[i + 1])
                            
                            cursor.execute("""
                                SELECT product_id, product_name, price FROM Products 
                                WHERE article=?
                            """, (art,))
                            product = cursor.fetchone()
                            
                            if product:
                                self.current_items.append({
                                    'product_id': product[0],
                                    'article': art,
                                    'name': product[1],
                                    'quantity': qty,
                                    'price': product[2]
                                })
            
            conn.close()
            self.update_items_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные заказа: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def generate_article(self):
        self.article_input.setText(f"ORD-{uuid.uuid4().hex[:8].upper()}")
    
    def add_item(self):
        if self.product_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")
            return
        
        product_id = self.product_combo.currentData()
        quantity = self.quantity_spin.value()
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT article, product_name, price, quantity FROM Products WHERE product_id=?", (product_id,))
            article, name, price, stock = cursor.fetchone()
            conn.close()
            
            if quantity > stock:
                QMessageBox.warning(self, "Ошибка", f"Недостаточно товара на складе. Доступно: {stock}")
                return
            
            for item in self.current_items:
                if item['product_id'] == product_id:
                    QMessageBox.warning(self, "Ошибка", "Товар уже добавлен в заказ")
                    return
            
            self.current_items.append({
                'product_id': product_id,
                'article': article,
                'name': name,
                'quantity': quantity,
                'price': price
            })
            
            self.update_items_table()
            self.quantity_spin.setValue(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить товар: {str(e)}")
    
    def remove_item(self, index):
        if 0 <= index < len(self.current_items):
            del self.current_items[index]
            self.update_items_table()
    
    def update_items_table(self):
        self.items_table.setRowCount(len(self.current_items))
        total = 0
        
        for row, item in enumerate(self.current_items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item['article']))
            self.items_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item['price']:.2f} ₽"))
            
            item_total = item['quantity'] * item['price']
            total += item_total
            
            remove_btn = QPushButton("Удалить")
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
            self.items_table.setCellWidget(row, 4, remove_btn)
        
        self.total_label.setText(f"{total:.2f} ₽")
    
    def save_order(self):
        if not self.order_id and not self.article_input.text():
            QMessageBox.warning(self, "Ошибка", "Введите артикул заказа")
            return
        
        # ИСПРАВЛЕНО: Проверяем выбор пункта выдачи
        if self.pickup_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите пункт выдачи")
            return
        
        if not self.current_items:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один товар в заказ")
            return
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            
            status_map = {0: 'new', 1: 'processing', 2: 'completed', 3: 'cancelled'}
            
            # Формируем строку с артикулами товаров
            article_parts = []
            for item in self.current_items:
                article_parts.append(item['article'])
                article_parts.append(str(item['quantity']))
            order_article = ', '.join(article_parts)
            
            if self.order_id:
                # ИСПРАВЛЕНО: Используем pickup_point_id вместо pickup_address
                cursor.execute("""
                    UPDATE Orders SET 
                        order_article=?, user_id=?, status=?, pickup_point_id=?, 
                        order_date=?, issue_date=?
                    WHERE order_id=?
                """, (
                    order_article,
                    self.client_combo.currentData(),
                    status_map[self.status_combo.currentIndex()],
                    self.pickup_combo.currentData(),
                    self.order_date.date().toString("yyyy-MM-dd"),
                    self.issue_date.date().toString("yyyy-MM-dd") if self.issue_date.date() else None,
                    self.order_id
                ))
            else:
                # ИСПРАВЛЕНО: Используем pickup_point_id вместо pickup_address
                cursor.execute("""
                    INSERT INTO Orders 
                    (order_article, user_id, status, pickup_point_id, order_date, issue_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    order_article,
                    self.client_combo.currentData(),
                    status_map[self.status_combo.currentIndex()],
                    self.pickup_combo.currentData(),
                    self.order_date.date().toString("yyyy-MM-dd"),
                    self.issue_date.date().toString("yyyy-MM-dd") if self.issue_date.date() else None
                ))
                
                self.order_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Успех", "Заказ успешно сохранен")
            
            if self.parent_view:
                self.parent_view.refresh_orders()
            
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить заказ: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def delete_order(self):
        try:
            reply = QMessageBox.question(self, "Подтверждение", 
                                        "Вы уверены, что хотите удалить заказ?",
                                        QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                conn = sqlite3.connect('shoe_store.db')
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM Orders WHERE order_id=?", (self.order_id,))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Успех", "Заказ успешно удален")
                
                if self.parent_view:
                    self.parent_view.refresh_orders()
                
                self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить заказ: {str(e)}")
    
    def closeEvent(self, event):
        if self in OrderEditWindow.edit_windows:
            OrderEditWindow.edit_windows.remove(self)
        event.accept()