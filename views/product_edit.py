from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QFileDialog, QSpinBox, QDoubleSpinBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import sqlite3
import os
from PIL import Image

class ProductEditWindow(QWidget):
    edit_windows = []
    
    def __init__(self, main_app, product_id=None, parent_view=None):
        super().__init__()
        
        if len(ProductEditWindow.edit_windows) > 0:
            QMessageBox.warning(self, "Внимание", "Окно редактирования уже открыто")
            self.close()
            return
            
        ProductEditWindow.edit_windows.append(self)
        
        self.main_app = main_app
        self.product_id = product_id
        self.parent_view = parent_view
        self.image_path = None
        self.current_image_file = None
        
        self.initUI()
        self.load_data()
        
    def initUI(self):
        self.setWindowTitle("ООО Обувь - " + ("Редактирование" if self.product_id else "Добавление") + " товара")
        self.setFixedSize(600, 750)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: 'Times New Roman';
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #7FFF00;
                border-radius: 4px;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton {
                background-color: #7FFF00;
                color: black;
                padding: 10px;
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
            QLabel {
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel(("Редактирование" if self.product_id else "Добавление") + " товара")
        title.setFont(QFont('Times New Roman', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        if self.product_id:
            id_layout = QHBoxLayout()
            id_layout.addWidget(QLabel("ID товара:"))
            self.id_label = QLabel(str(self.product_id))
            self.id_label.setStyleSheet("background-color: #f0f0f0; padding: 8px; border-radius: 4px;")
            id_layout.addWidget(self.id_label)
            id_layout.addStretch()
            layout.addLayout(id_layout)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(300, 200)
        self.image_label.setStyleSheet("border: 2px dashed #7FFF00;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.load_default_image()
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        
        image_btn = QPushButton("Загрузить изображение")
        image_btn.clicked.connect(self.load_image)
        layout.addWidget(image_btn)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        
        article_layout = QHBoxLayout()
        article_layout.addWidget(QLabel("Артикул:"))
        self.article_input = QLineEdit()
        self.article_input.setPlaceholderText("Артикул товара *")
        article_layout.addWidget(self.article_input)
        form_layout.addLayout(article_layout)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Наименование товара *")
        form_layout.addWidget(self.name_input)
        
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Категория:"))
        self.category_combo = QComboBox()
        category_layout.addWidget(self.category_combo)
        form_layout.addLayout(category_layout)
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Описание")
        form_layout.addWidget(self.desc_input)
        
        manufacturer_layout = QHBoxLayout()
        manufacturer_layout.addWidget(QLabel("Производитель:"))
        self.manufacturer_combo = QComboBox()
        manufacturer_layout.addWidget(self.manufacturer_combo)
        form_layout.addLayout(manufacturer_layout)
        
        supplier_layout = QHBoxLayout()
        supplier_layout.addWidget(QLabel("Поставщик:"))
        self.supplier_combo = QComboBox()
        supplier_layout.addWidget(self.supplier_combo)
        form_layout.addLayout(supplier_layout)
        
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel("Цена:"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999.99)
        self.price_input.setPrefix("₽ ")
        self.price_input.setSingleStep(10)
        price_layout.addWidget(self.price_input)
        form_layout.addLayout(price_layout)
        
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("Ед. изм.:"))
        self.unit_combo = QComboBox()
        unit_layout.addWidget(self.unit_combo)
        form_layout.addLayout(unit_layout)
        
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Количество:"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 999999)
        quantity_layout.addWidget(self.quantity_input)
        form_layout.addLayout(quantity_layout)
        
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("Скидка:"))
        self.discount_input = QSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setSuffix("%")
        discount_layout.addWidget(self.discount_input)
        form_layout.addLayout(discount_layout)
        
        layout.addLayout(form_layout)
        
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_product)
        buttons_layout.addWidget(save_btn)
        
        if self.product_id:
            delete_btn = QPushButton("Удалить товар")
            delete_btn.setProperty("class", "danger")
            delete_btn.clicked.connect(self.delete_product)
            buttons_layout.addWidget(delete_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        self.load_combo_data()
    
    def load_default_image(self):
        pixmap = QPixmap('assets/picture.png')
        if not pixmap.isNull():
            scaled = pixmap.scaled(280, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("Нет изображения")
    
    def load_combo_data(self):
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT category_id, category_name FROM Categories ORDER BY category_name")
            categories = cursor.fetchall()
            for cat_id, cat_name in categories:
                self.category_combo.addItem(cat_name, cat_id)
            
            cursor.execute("SELECT manufacturer_id, manufacturer_name FROM Manufacturers ORDER BY manufacturer_name")
            manufacturers = cursor.fetchall()
            for man_id, man_name in manufacturers:
                self.manufacturer_combo.addItem(man_name, man_id)
            
            cursor.execute("SELECT supplier_id, supplier_name FROM Suppliers ORDER BY supplier_name")
            suppliers = cursor.fetchall()
            for sup_id, sup_name in suppliers:
                self.supplier_combo.addItem(f"{sup_name} (ID: {sup_id})", sup_id)
            
            cursor.execute("SELECT unit_id, unit_name FROM Units ORDER BY unit_name")
            units = cursor.fetchall()
            for unit_id, unit_name in units:
                self.unit_combo.addItem(unit_name, unit_id)
            
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить справочники: {str(e)}")
    
    def load_data(self):
        if not self.product_id:
            return
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT article, product_name, category_id, description, manufacturer_id, 
                       supplier_id, price, unit_id, quantity, discount, image_path
                FROM Products WHERE product_id=?
            """, (self.product_id,))
            product = cursor.fetchone()
            conn.close()
            
            if product:
                article, name, cat_id, desc, man_id, sup_id, price, unit_id, qty, disc, img_path = product
                
                self.article_input.setText(article)
                self.name_input.setText(name)
                self.desc_input.setText(desc or "")
                
                index = self.category_combo.findData(cat_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                
                index = self.manufacturer_combo.findData(man_id)
                if index >= 0:
                    self.manufacturer_combo.setCurrentIndex(index)
                
                index = self.supplier_combo.findData(sup_id)
                if index >= 0:
                    self.supplier_combo.setCurrentIndex(index)
                
                self.price_input.setValue(price)
                
                index = self.unit_combo.findData(unit_id)
                if index >= 0:
                    self.unit_combo.setCurrentIndex(index)
                
                self.quantity_input.setValue(qty)
                self.discount_input.setValue(disc)
                
                if img_path:
                    self.current_image_file = img_path
                    full_path = os.path.join('product_images', img_path)
                    if os.path.exists(full_path):
                        pixmap = QPixmap(full_path)
                        if not pixmap.isNull():
                            scaled = pixmap.scaled(280, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            self.image_label.setPixmap(scaled)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные товара: {str(e)}")
    
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        
        if file_path:
            try:
                img = Image.open(file_path)
                img.thumbnail((300, 200), Image.Resampling.LANCZOS)
                
                if not os.path.exists('product_images'):
                    os.makedirs('product_images')
                
                if self.product_id:
                    _, ext = os.path.splitext(file_path)
                    new_filename = f"product_{self.product_id}{ext}"
                else:
                    new_filename = f"temp_{os.path.basename(file_path)}"
                
                new_path = os.path.join('product_images', new_filename)
                
                img.save(new_path)
                
                if self.current_image_file and os.path.exists(os.path.join('product_images', self.current_image_file)):
                    try:
                        os.remove(os.path.join('product_images', self.current_image_file))
                    except:
                        pass
                
                self.current_image_file = new_filename
                
                pixmap = QPixmap(new_path)
                scaled = pixmap.scaled(280, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled)
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение: {str(e)}")
    
    def save_product(self):
        if not self.article_input.text():
            QMessageBox.warning(self, "Ошибка", "Артикул товара обязателен")
            return
        
        if not self.name_input.text():
            QMessageBox.warning(self, "Ошибка", "Наименование товара обязательно")
            return
        
        if self.category_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию")
            return
        
        if self.manufacturer_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите производителя")
            return
        
        if self.supplier_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите поставщика")
            return
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            
            if self.product_id:
                cursor.execute("""
                    UPDATE Products SET 
                        article=?, product_name=?, category_id=?, description=?, 
                        manufacturer_id=?, supplier_id=?, price=?, unit_id=?, 
                        quantity=?, discount=?, image_path=?
                    WHERE product_id=?
                """, (
                    self.article_input.text(),
                    self.name_input.text(),
                    self.category_combo.currentData(),
                    self.desc_input.text() or None,
                    self.manufacturer_combo.currentData(),
                    self.supplier_combo.currentData(),
                    self.price_input.value(),
                    self.unit_combo.currentData(),
                    self.quantity_input.value(),
                    self.discount_input.value(),
                    self.current_image_file,
                    self.product_id
                ))
                message = "Товар успешно обновлен"
            else:
                cursor.execute("""
                    INSERT INTO Products 
                    (article, product_name, category_id, description, manufacturer_id, 
                     supplier_id, price, unit_id, quantity, discount, image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.article_input.text(),
                    self.name_input.text(),
                    self.category_combo.currentData(),
                    self.desc_input.text() or None,
                    self.manufacturer_combo.currentData(),
                    self.supplier_combo.currentData(),
                    self.price_input.value(),
                    self.unit_combo.currentData(),
                    self.quantity_input.value(),
                    self.discount_input.value(),
                    self.current_image_file
                ))
                
                self.product_id = cursor.lastrowid
                message = "Товар успешно добавлен"
                
                if self.current_image_file and 'temp_' in self.current_image_file:
                    _, ext = os.path.splitext(self.current_image_file)
                    new_filename = f"product_{self.product_id}{ext}"
                    old_path = os.path.join('product_images', self.current_image_file)
                    new_path = os.path.join('product_images', new_filename)
                    try:
                        os.rename(old_path, new_path)
                        self.current_image_file = new_filename
                        
                        cursor.execute("UPDATE Products SET image_path=? WHERE product_id=?", 
                                     (new_filename, self.product_id))
                    except Exception as e:
                        print(f"Ошибка переименования файла: {e}")
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Успех", message)
            
            if self.parent_view:
                self.parent_view.refresh_products()
            
            self.close()
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                QMessageBox.critical(self, "Ошибка", "Товар с таким артикулом уже существует")
            else:
                QMessageBox.critical(self, "Ошибка целостности", f"Нарушение целостности данных: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить товар: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def delete_product(self):
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM Orders WHERE order_article LIKE ?", (f"%{self.article_input.text()}%",))
            count = cursor.fetchone()[0]
            
            if count > 0:
                QMessageBox.warning(self, "Невозможно удалить", 
                                   "Товар присутствует в заказах и не может быть удален")
                conn.close()
                return
            
            reply = QMessageBox.question(self, "Подтверждение", 
                                        "Вы уверены, что хотите удалить товар?",
                                        QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                cursor.execute("DELETE FROM Products WHERE product_id=?", (self.product_id,))
                conn.commit()
                
                if self.current_image_file:
                    try:
                        os.remove(os.path.join('product_images', self.current_image_file))
                    except:
                        pass
                
                QMessageBox.information(self, "Успех", "Товар успешно удален")
                
                if self.parent_view:
                    self.parent_view.refresh_products()
                
                self.close()
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить товар: {str(e)}")
    
    def closeEvent(self, event):
        if self in ProductEditWindow.edit_windows:
            ProductEditWindow.edit_windows.remove(self)
        event.accept()