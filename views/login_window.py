from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import sqlite3
import os
from views.product_list import ProductListWindow
from views.client_view import ClientView
from views.manager_view import ManagerView
from views.admin_view import AdminView
from database.import_from_excel import import_all_data
from database.init_db import create_database

class LoginWindow(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.initUI()
        
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
                font-weight: bold;
                min-width: 150px;
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
            QPushButton.warning {
                background-color: #FFA500;
            }
            QPushButton.warning:hover {
                background-color: #FF8C00;
            }
            QFrame {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 15px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        logo_label = QLabel()
        pixmap = QPixmap('assets/logo.png')
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(logo_label)
        
        title = QLabel("ООО Обувь")
        title.setFont(QFont('Times New Roman', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2E8B57; margin-bottom: 10px;")
        content_layout.addWidget(title)
        
        login_frame = QFrame()
        login_frame.setFrameStyle(QFrame.Box)
        login_frame.setLineWidth(2)
        login_layout = QVBoxLayout(login_frame)
        login_layout.setSpacing(10)
        
        login_label = QLabel("Вход в систему")
        login_label.setFont(QFont('Times New Roman', 16, QFont.Bold))
        login_label.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(login_label)
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        login_layout.addWidget(self.login_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        login_layout.addWidget(self.password_input)
        
        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.login)
        login_layout.addWidget(login_button)
        
        guest_button = QPushButton("Войти как гость")
        guest_button.setStyleSheet("background-color: #00FA9A;")
        guest_button.clicked.connect(self.login_as_guest)
        login_layout.addWidget(guest_button)
        
        content_layout.addWidget(login_frame)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #7FFF00; max-height: 2px;")
        content_layout.addWidget(separator)
        
        db_frame = QFrame()
        db_frame.setFrameStyle(QFrame.Box)
        db_frame.setLineWidth(2)
        db_layout = QVBoxLayout(db_frame)
        db_layout.setSpacing(10)
        
        db_label = QLabel("Управление базой данных")
        db_label.setFont(QFont('Times New Roman', 14, QFont.Bold))
        db_label.setAlignment(Qt.AlignCenter)
        db_layout.addWidget(db_label)
        
        info_label = QLabel(
            "Excel файлы должны находиться в папке 'db_init':\n"
            "pick_points.xlsx, products.xlsx, users.xlsx, orders.xlsx"
        )
        info_label.setFont(QFont('Times New Roman', 9))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666;")
        info_label.setWordWrap(True)
        db_layout.addWidget(info_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        import_btn = QPushButton("📥 Импорт из Excel")
        import_btn.setStyleSheet("background-color: #00FA9A;")
        import_btn.clicked.connect(self.import_data)
        button_layout.addWidget(import_btn)
        
        clear_btn = QPushButton("🗑️ Очистить БД")
        clear_btn.setStyleSheet("background-color: #ff6b6b;")
        clear_btn.clicked.connect(self.clear_database)
        button_layout.addWidget(clear_btn)
        
        db_layout.addLayout(button_layout)
        content_layout.addWidget(db_frame)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def login(self):
        login = self.login_input.text()
        password = self.password_input.text()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, full_name, role FROM Users WHERE login=? AND password=?", (login, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_data = {'id': user[0], 'name': user[1], 'role': user[2]}
                self.main_app.set_user(user_data)
                
                if user[2] == 'admin':
                    self.main_app.stacked_widget.addWidget(AdminView(self.main_app))
                    self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.count() - 1)
                elif user[2] == 'manager':
                    self.main_app.stacked_widget.addWidget(ManagerView(self.main_app))
                    self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.count() - 1)
                else:
                    self.main_app.stacked_widget.addWidget(ClientView(self.main_app))
                    self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.count() - 1)
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка базы данных", str(e))
    
    def login_as_guest(self):
        user_data = {'id': None, 'name': 'Гость', 'role': 'guest'}
        self.main_app.set_user(user_data)
        self.main_app.stacked_widget.addWidget(ProductListWindow(self.main_app))
        self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.count() - 1)
    
    def import_data(self):
        if not os.path.exists('db_init'):
            QMessageBox.warning(self, "Ошибка", "Папка 'db_init' не найдена")
            return
        
        required_files = ['pick_points.xlsx', 'products.xlsx', 'users.xlsx', 'orders.xlsx']
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join('db_init', file)):
                missing_files.append(file)
        
        if missing_files:
            QMessageBox.warning(self, "Ошибка", 
                               f"Отсутствуют файлы:\n{', '.join(missing_files)}\n\n"
                               "Поместите все файлы в папку 'db_init'")
            return
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение",
            "Импорт данных из Excel файлов.\n\n"
            "ВНИМАНИЕ: Все существующие данные будут заменены!\n\n"
            "Продолжить?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            create_database()
            success = import_all_data()
            
            if success:
                QMessageBox.information(self, "Успех", 
                                      "Данные успешно импортированы из Excel файлов!")
                if os.path.exists('db_initialized.flag'):
                    os.remove('db_initialized.flag')
            else:
                QMessageBox.critical(self, "Ошибка", 
                                   "Произошла ошибка при импорте данных.\n"
                                   "Проверьте консоль для подробностей.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при импорте: {str(e)}")
    
    def clear_database(self):
        reply = QMessageBox.question(
            self, 
            "Подтверждение",
            "ОЧИСТКА БАЗЫ ДАННЫХ\n\n"
            "ВНИМАНИЕ: Все данные будут безвозвратно удалены!\n\n"
            "Вы уверены?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        reply2 = QMessageBox.question(
            self, 
            "Последнее подтверждение",
            "Это последнее предупреждение!\n"
            "Все товары, заказы и пользователи будут удалены.\n\n"
            "Точно продолжить?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply2 == QMessageBox.No:
            return
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            for table in tables:
                table_name = table[0]
                if table_name != 'sqlite_sequence':
                    try:
                        cursor.execute(f"DELETE FROM {table_name}")
                    except Exception as e:
                        print(f"Ошибка при очистке {table_name}: {e}")
            
            cursor.execute("DELETE FROM sqlite_sequence")
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            conn.close()
            
            if os.path.exists('db_initialized.flag'):
                os.remove('db_initialized.flag')
            
            QMessageBox.information(self, "Успех", "База данных успешно очищена!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при очистке БД: {str(e)}")