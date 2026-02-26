from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3

class SupplierEditWindow(QWidget):
    def __init__(self, main_app, supplier_id=None, parent_view=None):
        super().__init__()
        self.main_app = main_app
        self.supplier_id = supplier_id
        self.parent_view = parent_view
        self.setWindowTitle("ООО Обувь - " + ("Редактирование" if self.supplier_id else "Добавление") + " поставщика")
        self.setFixedSize(400, 200)
        self.setWindowModality(Qt.ApplicationModal)  # Делаем окно модальным
        self.initUI()
        self.load_data()
        
    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: 'Times New Roman';
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #7FFF00;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #7FFF00;
                color: black;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00FA9A;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel(("Редактирование" if self.supplier_id else "Добавление") + " поставщика")
        title.setFont(QFont('Times New Roman', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название поставщика *")
        form_layout.addWidget(self.name_input)
        
        layout.addLayout(form_layout)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_supplier)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        if not self.supplier_id:
            return
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT supplier_name FROM Suppliers WHERE supplier_id=?", (self.supplier_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                self.name_input.setText(result[0])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def save_supplier(self):
        supplier_name = self.name_input.text().strip()
        
        if not supplier_name:
            QMessageBox.warning(self, "Ошибка", "Введите название поставщика")
            self.name_input.setFocus()
            return
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            
            if self.supplier_id:
                cursor.execute("UPDATE Suppliers SET supplier_name=? WHERE supplier_id=?", 
                             (supplier_name, self.supplier_id))
                message = "Поставщик успешно обновлен"
            else:
                cursor.execute("INSERT INTO Suppliers (supplier_name) VALUES (?)", 
                             (supplier_name,))
                message = "Поставщик успешно добавлен"
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Успех", message)
            
            if self.parent_view:
                self.parent_view.load_suppliers()  # Обновляем таблицу
                if hasattr(self.parent_view, 'parent_view') and self.parent_view.parent_view:
                    self.parent_view.parent_view.refresh_suppliers()  # Обновляем фильтр в админке
            
            self.close()
            
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Ошибка", "Поставщик с таким названием уже существует")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить поставщика: {str(e)}")