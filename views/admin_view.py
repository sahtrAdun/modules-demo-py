from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
import sqlite3
from views.manager_view import ManagerView
from views.product_edit import ProductEditWindow
from views.supplier_manager import SupplierManagerWindow

class AdminView(ManagerView):
    def __init__(self, main_app):
        super().__init__(main_app)
        self.setWindowTitle("ООО Обувь - Администратор")
        
    def initUI(self):
        super().initUI()
        
        admin_buttons_layout = QHBoxLayout()
        
        add_product_btn = QPushButton("Добавить товар")
        add_product_btn.setStyleSheet("background-color: #00FA9A; font-weight: bold;")
        add_product_btn.clicked.connect(self.add_product)
        admin_buttons_layout.addWidget(add_product_btn)
        
        add_supplier_btn = QPushButton("Управление поставщиками")
        add_supplier_btn.setStyleSheet("background-color: #7FFF00;")
        add_supplier_btn.clicked.connect(self.open_supplier_manager)
        admin_buttons_layout.addWidget(add_supplier_btn)
        
        admin_buttons_layout.addStretch()
        
        layout = self.layout()
        layout.insertLayout(2, admin_buttons_layout)
        
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.itemDoubleClicked.connect(self.edit_product)
        
        self.load_original_products()
    
    def add_product(self):
        self.edit_window = ProductEditWindow(self.main_app, None, self)
        self.edit_window.show()
    
    def open_supplier_manager(self):
        self.supplier_manager = SupplierManagerWindow(self.main_app, self)
        self.supplier_manager.show()
    
    def edit_product(self, item):
        row = item.row()
        article = self.table.item(row, 1).text()
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT product_id FROM Products WHERE article=?", (article,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                self.edit_window = ProductEditWindow(self.main_app, result[0], self)
                self.edit_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть товар: {str(e)}")
    
    def refresh_products(self):
        self.load_original_products()
        self.apply_filters()
    
    def refresh_suppliers(self):
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT supplier_name FROM Suppliers ORDER BY supplier_name")
            suppliers = cursor.fetchall()
            conn.close()
            
            current_text = self.supplier_combo.currentText()
            self.supplier_combo.clear()
            self.supplier_combo.addItem("Все поставщики")
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier[0])
            
            index = self.supplier_combo.findText(current_text)
            if index >= 0:
                self.supplier_combo.setCurrentIndex(index)
        except Exception as e:
            print(f"Ошибка обновления списка поставщиков: {e}")