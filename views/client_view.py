from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from views.product_list import ProductListWindow

class ClientView(ProductListWindow):
    def __init__(self, main_app):
        super().__init__(main_app)
        self.setWindowTitle("ООО Обувь - Клиент")
        
    def initUI(self):
        super().initUI()
        
        info_label = QLabel("Режим авторизованного клиента - просмотр товаров")
        info_label.setFont(QFont('Times New Roman', 12))
        info_label.setStyleSheet("color: #2E8B57; padding: 10px;")
        
        layout = self.layout()
        layout.insertWidget(1, info_label)
