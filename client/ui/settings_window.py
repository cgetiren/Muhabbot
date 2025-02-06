from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea,
                            QLabel, QComboBox, QSlider, QPushButton,
                            QRadioButton, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEvent, QSize
from PyQt6.QtGui import QIcon
import pyaudio

class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.p = pyaudio.PyAudio()
        self.init_ui()
        self.setup_animations()
        
        # Event filter'ı ekle
        if parent:
            parent.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Panel dışına tıklanınca paneli kapat"""
        if event.type() == QEvent.Type.MouseButtonPress:
            if obj == self.parent():
                # Tıklanan pozisyonu al
                pos = event.pos()
                # Eğer tıklama panel dışındaysa paneli kapat
                if not self.geometry().contains(pos):
                    self.hide_panel()
                    return True
        return super().eventFilter(obj, event)

    def init_ui(self):
        # Panel genişliğini ayarla
        self.setFixedWidth(450)
        self.setContentsMargins(0, 0, 0, 0)  # Tüm kenar boşluklarını sıfırla
        
        # Ana layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Başlık ve çarpı butonu için container
        header = QWidget()
        header.setStyleSheet("background-color: #2f3136;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 16)
        
        title = QLabel("Ses Ayarları")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
        close_button = QPushButton()
        close_button.setIcon(QIcon("client/assets/close.png"))
        close_button.setIconSize(QSize(16, 16))
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #40444b;
                border-radius: 4px;
            }
        """)
        close_button.clicked.connect(self.hide_panel)
        
        header_layout.addWidget(title)
        header_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(header)
        
        # Scroll area ve içerik
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #2f3136; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(16, 16, 16, 16)
        
        # Giriş Aygıtı (Varsayılan)
        input_title = QLabel("Giriş Aygıtı")
        input_title.setStyleSheet("color: #dcddde;")
        self.mic_combo = QComboBox()
        self.load_input_devices()
        content_layout.addWidget(input_title)
        content_layout.addWidget(self.mic_combo)
        
        # Çıkış Aygıtı (Varsayılan)
        output_title = QLabel("Çıkış Aygıtı")
        output_title.setStyleSheet("color: #dcddde;")
        self.speaker_combo = QComboBox()
        self.load_output_devices()
        content_layout.addWidget(output_title)
        content_layout.addWidget(self.speaker_combo)
        
        # Giriş Sesi
        input_vol_title = QLabel("Giriş Sesi")
        input_vol_title.setStyleSheet("color: #dcddde;")
        self.mic_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.mic_volume_slider.setRange(0, 100)
        self.mic_volume_slider.setValue(80)
        content_layout.addWidget(input_vol_title)
        content_layout.addWidget(self.mic_volume_slider)
        
        # Çıkış Sesi
        output_vol_title = QLabel("Çıkış Sesi")
        output_vol_title.setStyleSheet("color: #dcddde;")
        self.speaker_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.speaker_volume_slider.setRange(0, 100)
        self.speaker_volume_slider.setValue(80)
        content_layout.addWidget(output_vol_title)
        content_layout.addWidget(self.speaker_volume_slider)
        
        # Mikrofon Testi
        mic_test_title = QLabel("Mikrofon Testi")
        mic_test_desc = QLabel("Mikrofonunda sorun mu var? Bir test yap ve komik bir şey söyle, sonra sesini sana dinleteceğiz.")
        mic_test_desc.setWordWrap(True)
        mic_test_desc.setStyleSheet("color: #8e9297; font-size: 12px;")
        self.test_button = QPushButton("Kontrol Edelim")
        self.test_button.clicked.connect(self.test_microphone)
        
        content_layout.addWidget(mic_test_title)
        content_layout.addWidget(mic_test_desc)
        content_layout.addWidget(self.test_button)
        
        # Ayırıcı çizgi
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #40444b;")
        content_layout.addWidget(line)
        
        # Giriş Modu
        input_mode_title = QLabel("Giriş Modu")
        self.voice_activity = QRadioButton("Ses Etkinliği")
        self.push_to_talk = QRadioButton("Bas-Konuş")
        self.voice_activity.setChecked(True)
        
        content_layout.addWidget(input_mode_title)
        content_layout.addWidget(self.voice_activity)
        content_layout.addWidget(self.push_to_talk)
        
        # Giriş Duyarlılığı
        sensitivity_title = QLabel("Giriş Duyarlılığı")
        sensitivity_desc = QLabel("Giriş hassasiyetini otomatik olarak belirle")
        sensitivity_desc.setStyleSheet("color: #8e9297; font-size: 12px;")
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(0, 100)
        self.sensitivity_slider.setValue(50)
        
        content_layout.addWidget(sensitivity_title)
        content_layout.addWidget(sensitivity_desc)
        content_layout.addWidget(self.sensitivity_slider)
        
        # Yardım linki
        help_text = QLabel('Ses veya videoyla ilgili yardıma mı ihtiyacın var? <a href="https://support.discord.com" style="color: #00b0f4;">Sorun giderme rehberimize</a> göz at.')
        help_text.setOpenExternalLinks(True)
        help_text.setStyleSheet("color: #8e9297; font-size: 12px;")
        content_layout.addWidget(help_text)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def setup_animations(self):
        """Panel animasyonlarını ayarla"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
    
    def show_panel(self):
        """Paneli sağdan aç"""
        parent = self.parent()
        if parent:
            # Tam sağdan başla
            start_x = parent.width()
            # Bitiş pozisyonu: Panel genişliği kadar sola
            end_x = parent.width() - self.width()
            
            # Paneli başlangıçta tam sağa konumlandır
            self.move(start_x, 0)
            
            # Animasyonu ayarla
            self.animation.setStartValue(QRect(start_x, 0, self.width(), parent.height()))
            self.animation.setEndValue(QRect(end_x, 0, self.width(), parent.height()))
            
            self.raise_()
            self.show()
            self.animation.start()

    def hide_panel(self):
        """Paneli sağa doğru kapat"""
        parent = self.parent()
        if parent:
            # Başlangıç pozisyonu: Mevcut konum
            start_x = self.x()
            # Bitiş pozisyonu: Tam sağ kenar
            end_x = parent.width()
            
            self.animation.setStartValue(QRect(start_x, 0, self.width(), parent.height()))
            self.animation.setEndValue(QRect(end_x, 0, self.width(), parent.height()))
            
            try:
                self.animation.finished.disconnect()
            except TypeError:
                pass
                
            self.animation.finished.connect(self.on_hide_finished)
            self.animation.start()
    
    def on_hide_finished(self):
        """Panel kapandıktan sonra"""
        self.hide()
        try:
            self.animation.finished.disconnect()
        except TypeError:
            pass

    def load_input_devices(self):
        """Varsayılan mikrofon ve diğer cihazları yükle"""
        self.mic_combo.clear()
        default_input = self.p.get_default_input_device_info()
        self.mic_combo.addItem(f"{default_input['name']} (Varsayılan)", default_input['index'])
        
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0 and i != default_input['index']:
                self.mic_combo.addItem(device_info['name'], i)

    def load_output_devices(self):
        """Varsayılan hoparlör ve diğer cihazları yükle"""
        self.speaker_combo.clear()
        default_output = self.p.get_default_output_device_info()
        self.speaker_combo.addItem(f"{default_output['name']} (Varsayılan)", default_output['index'])
        
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0 and i != default_output['index']:
                self.speaker_combo.addItem(device_info['name'], i)

    def test_microphone(self):
        """Mikrofon test fonksiyonu - Gerçek zamanlı ses dinleme"""
        if hasattr(self.parent(), 'audio_manager'):
            if self.test_button.text() == "Kontrol Edelim":
                # Test başlat
                self.test_button.setText("Testi Bitir")
                self.test_button.setStyleSheet("background-color: #ed4245;") # Kırmızı buton
                
                # Ses çıkışını direkt mikrofona yönlendir
                self.parent().audio_manager.start_microphone_loopback()
            else:
                # Testi durdur
                self.test_button.setText("Kontrol Edelim")
                self.test_button.setStyleSheet("") # Normal stil
                
                # Loopback'i durdur
                self.parent().audio_manager.stop_microphone_loopback()

    def get_settings(self):
        """Ayarları döndür"""
        return {
            'input_device': self.mic_combo.currentData(),
            'output_device': self.speaker_combo.currentData(),
            'mic_volume': self.mic_volume_slider.value(),
            'speaker_volume': self.speaker_volume_slider.value(),
            'input_mode': 'voice_activity' if self.voice_activity.isChecked() else 'push_to_talk',
            'sensitivity': self.sensitivity_slider.value()
        }
