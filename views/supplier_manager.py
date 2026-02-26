from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3
from views.supplier_edit import SupplierEditWindow

class SupplierManagerWindow(QWidget):
    def __init__(self, main_app, parent_view=None):
        super().__init__()
        self.main_app = main_app
        self.parent_view = parent_view
        self.setWindowTitle("ООО Обувь - Управление поставщиками")
        self.setFixedSize(600, 400)
        self.initUI()
        self.load_suppliers()
        
    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: 'Times New Roman';
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
            QPushButton {
                background-color: #7FFF00;
                color: black;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00FA9A;
            }
            QPushButton.delete {
                background-color: #ff6b6b;
            }
            QPushButton.delete:hover {
                background-color: #ff5252;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Управление поставщиками")
        title.setFont(QFont('Times New Roman', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Добавить поставщика")
        add_btn.clicked.connect(self.add_supplier)
        buttons_layout.addWidget(add_btn)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Таблица поставщиков
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Название поставщика", "Действия"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_suppliers(self):
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT supplier_id, supplier_name FROM Suppliers ORDER BY supplier_name")
            suppliers = cursor.fetchall()
            conn.close()
            
            self.table.setRowCount(len(suppliers))
            
            for row, (supplier_id, supplier_name) in enumerate(suppliers):
                # ID
                self.table.setItem(row, 0, QTableWidgetItem(str(supplier_id)))
                
                # Название
                self.table.setItem(row, 1, QTableWidgetItem(supplier_name))
                
                # Кнопки действий
                buttons_widget = QWidget()
                buttons_layout = QHBoxLayout()
                buttons_layout.setContentsMargins(2, 2, 2, 2)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_supplier(r))
                buttons_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("🗑️")
                delete_btn.setProperty("class", "delete")
                delete_btn.setFixedSize(30, 30)
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_supplier(r))
                buttons_layout.addWidget(delete_btn)
                
                buttons_widget.setLayout(buttons_layout)
                self.table.setCellWidget(row, 2, buttons_widget)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить поставщиков: {str(e)}")
    
    def add_supplier(self):
        self.edit_window = SupplierEditWindow(self.main_app, None, self)
        self.edit_window.show()
        self.edit_window.raise_()
    
    def edit_supplier(self, row):
        supplier_id = int(self.table.item(row, 0).text())
        self.edit_window = SupplierEditWindow(self.main_app, supplier_id, self)
        self.edit_window.show()
        self.edit_window.raise_()
    
    def delete_supplier(self, row):
        supplier_id = int(self.table.item(row, 0).text())
        supplier_name = self.table.item(row, 1).text()
        
        try:
            # Проверяем, есть ли товары с этим поставщиком
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Products WHERE supplier_id=?", (supplier_id,))
            count = cursor.fetchone()[0]
            conn.close()
            
            if count > 0:
                QMessageBox.warning(self, "Невозможно удалить", 
                                   f"Поставщик '{supplier_name}' используется в {count} товарах")
                return
            
            reply = QMessageBox.question(self, "Подтверждение", 
                                        f"Удалить поставщика '{supplier_name}'?",
                                        QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                conn = sqlite3.connect('shoe_store.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Suppliers WHERE supplier_id=?", (supplier_id,))
                conn.commit()
                conn.close()
                
                self.load_suppliers()
                if self.parent_view:
                    self.parent_view.refresh_suppliers()
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
