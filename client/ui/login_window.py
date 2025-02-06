from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QLineEdit, QPushButton)
from PyQt6.QtCore import Qt
from .main_window import MainWindow  # Dosyanın başına ekleyin

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Ana pencere ayarları
        self.setWindowTitle("Voice Chat - Giriş")
        self.setFixedSize(300, 150)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Kullanıcı adı alanı
        self.username_label = QLabel("Kullanıcı Adı:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcıadı")
        
        # Giriş butonu
        self.login_button = QPushButton("Katıl")
        self.login_button.clicked.connect(self.handle_login)
        
        # Layout'a widget'ları ekleme
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.login_button)
        
        # Boşluk ekleyerek düzen
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
    def handle_login(self):
        username = self.username_input.text().strip()
        if username:
            self.main_window = MainWindow(username)
            self.main_window.show()
            self.close()
        else:
            # TODO: Hata mesajı göster
            print("Kullanıcı adı boş olamaz!")
