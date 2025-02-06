import sys
import traceback
from PyQt6.QtWidgets import QApplication
from client.ui.login_window import LoginWindow  # Absolute import kullanıyoruz

def main():
    try:
        app = QApplication(sys.argv)
        
        # Stil ayarları
        app.setStyle('Fusion')
        
        # Login penceresini oluştur ve göster
        login_window = LoginWindow()
        login_window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        print("Hata oluştu:")
        print(f"Hata mesajı: {str(e)}")
        print("\nHata detayları:")
        traceback.print_exc()
        input("Devam etmek için bir tuşa basın...")  # Terminal kapanmasın diye

if __name__ == "__main__":
    main()
