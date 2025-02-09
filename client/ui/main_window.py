from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QListWidget, QTextEdit)
from PyQt6.QtCore import Qt, QTimer, QSize
from client.network.client_socket import ClientSocket
from client.audio.audio_manager import AudioManager
from client.ui.settings_window import SettingsPanel
import numpy as np
from datetime import datetime
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QEvent
from pathlib import Path

ASSETS_PATH = Path(__file__).resolve().parent.parent / "assets"

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.socket = ClientSocket()
        self.audio_manager = AudioManager()
        self.is_muted = False
        self.current_user_label = None
        
        # Ses durumu için timer
        self.voice_timer = QTimer()
        self.voice_timer.timeout.connect(self.reset_voice_indicator)
        
        # Önce UI'ı oluştur
        self.init_ui()
        
        # Sonra socket ve audio bağlantılarını kur
        self.setup_socket()
        self.setup_audio()
        
        # Server'a bağlan ama kanala otomatik katılma
        self.connect_to_server()
        
        # Ayarlar panelini oluştur
        self.settings_panel = SettingsPanel(self)
        self.settings_panel.hide()
        
    def init_ui(self):
        # Ana pencere ayarları
        self.setWindowTitle(f"Voice Chat - {self.username}")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #36393f;
            }
            QLabel {
                color: #ffffff;
            }
            QListWidget {
                background-color: #2f3136;
                border: none;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #40444b;
                border: none;
                color: #ffffff;
            }
        """)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sol panel (kanallar)
        left_panel = QWidget()
        left_panel.setFixedWidth(240)
        left_panel.setStyleSheet("background-color: #2f3136;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Kanallar başlığı
        channels_header = QWidget()
        channels_header.setStyleSheet("background-color: #2f3136; padding: 10px;")
        channels_header_layout = QVBoxLayout(channels_header)
        channels_label = QLabel("KANALLAR")
        channels_label.setStyleSheet("color: #8e9297; font-size: 12px; font-weight: bold;")
        channels_header_layout.addWidget(channels_label)
        
        # Kanallar listesi
        self.channels_widget = QWidget()
        self.channels_layout = QVBoxLayout(self.channels_widget)
        self.channels_layout.setSpacing(2)
        self.channels_layout.setContentsMargins(8, 0, 8, 0)
        
        # Her kanal için widget ve kullanıcı listesi oluştur
        self.channel_widgets = {}
        self.init_channel_widgets()
        
        # Sağ panel (sohbet)
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #36393f;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sohbet alanı
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #36393f;
                color: #dcddde;
                border: none;
                padding: 16px;
                font-size: 14px;
            }
        """)
        
        # Mesaj gönderme alanı
        message_panel = QWidget()
        message_panel.setFixedHeight(70)
        message_panel.setStyleSheet("""
            QWidget {
                background-color: #40444b;
                border-radius: 4px;
                margin: 0 16px 16px 16px;
            }
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #ffffff;
                padding: 8px;
                font-size: 14px;
            }
        """)
        message_layout = QHBoxLayout(message_panel)
        message_layout.setContentsMargins(8, 8, 8, 8)
        
        # Mesaj input alanı
        self.message_input = QTextEdit()
        self.message_input.setFixedHeight(50)
        self.message_input.setPlaceholderText("Mesaj gönder...")
        self.message_input.installEventFilter(self)  # Enter tuşu için
        
        message_layout.addWidget(self.message_input)
        
        right_layout.addWidget(self.chat_area)
        right_layout.addWidget(message_panel)
        
        # Alt panel (kullanıcı kontrolü)
        bottom_panel = QWidget()
        bottom_panel.setStyleSheet("""
            QWidget {
                background-color: #292b2f;
                color: #ffffff;
            }
        """)
        bottom_layout = QHBoxLayout(bottom_panel)
        
        # Kullanıcı etiketi
        self.user_label = QLabel(self.username)
        self.user_label.setStyleSheet("color: #ffffff;")
        
        # Ayarlar butonu
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon(str(ASSETS_PATH / "settings.png")))
        self.settings_button.setIconSize(QSize(20, 20))
        self.settings_button.setFixedSize(32, 32)
        self.settings_button.setToolTip("Ses Ayarları")
        self.settings_button.clicked.connect(self.toggle_settings_panel)
        self.settings_button.setStyleSheet("""
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
        
        bottom_layout.addWidget(self.user_label)
        bottom_layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Layout'ları birleştir
        left_layout.addWidget(channels_header)
        left_layout.addWidget(self.channels_widget)
        left_layout.addStretch()
        left_layout.addWidget(bottom_panel)
        
        # Ana layout'a panelleri ekle
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
    def init_channel_widgets(self):
        for channel in ["Genel Sohbet", "Oyun Odası", "Müzik Odası"]:
            # Kanal container
            channel_container = QWidget()
            channel_layout = QVBoxLayout(channel_container)
            channel_layout.setSpacing(0)
            channel_layout.setContentsMargins(0, 0, 0, 0)
            
            # Kanal başlığı container'ı
            header_container = QWidget()
            header_layout = QHBoxLayout(header_container)
            header_layout.setSpacing(4)
            header_layout.setContentsMargins(8, 4, 8, 4)
            
            # Kanal butonu
            channel_button = QPushButton(f"🔊 {channel}")
            channel_button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px;
                    background-color: transparent;
                    color: #8e9297;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #36393f;
                    color: #dcddde;
                }
                QPushButton[active="true"] {
                    background-color: #42464D;
                    color: white;
                }
            """)
            channel_button.clicked.connect(lambda checked, name=channel: self.join_channel(name))
            
            # Ayrıl butonu
            leave_button = QPushButton()
            leave_button.setIcon(QIcon("client/assets/leave.png"))
            leave_button.setFixedSize(24, 24)
            leave_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #36393f;
                    border-radius: 4px;
                }
            """)
            leave_button.clicked.connect(lambda checked, name=channel: self.leave_channel(name))
            leave_button.hide()
            
            header_layout.addWidget(channel_button)
            header_layout.addWidget(leave_button)
            
            channel_layout.addWidget(header_container)
            
            # Kullanıcı listesi widget'ı
            users_container = QWidget()
            users_container.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                }
            """)
            users_layout = QVBoxLayout(users_container)
            users_layout.setSpacing(2)
            users_layout.setContentsMargins(20, 0, 0, 0)  # Sol margin için
            
            channel_layout.addWidget(users_container)
            
            # Kanal bilgilerini sakla
            self.channel_widgets[channel] = {
                'container': channel_container,
                'button': channel_button,
                'leave_button': leave_button,
                'users_container': users_container,
                'users_layout': users_layout,
                'users': {}
            }
            
            self.channels_layout.addWidget(channel_container)

    def setup_socket(self):
        """Socket sinyallerini bağla"""
        self.socket.message_received.connect(self.handle_message)
        self.socket.user_joined.connect(self.handle_user_joined)
        self.socket.user_left.connect(self.handle_user_left)
        self.socket.audio_received.connect(self.handle_received_audio)
        
    def connect_to_server(self):
        if self.socket.connect_to_server():
            response = self.socket.login(self.username)
            if response['status'] == 'success':
                print("Giriş başarılı!")
                
    def join_channel(self, channel_name):
        """Kanala katıl"""
        if self.socket.current_room:
            self.leave_current_channel()
        
        print(f"\n[DEBUG] Attempting to join channel: {channel_name}")
        response = self.socket.join_room(channel_name)
        print(f"[DEBUG] Join response: {response}")
        
        if response and response.get('status') == 'success':
            # Kanal butonlarını güncelle
            for ch_name, ch_widgets in self.channel_widgets.items():
                ch_widgets['button'].setProperty('active', ch_name == channel_name)
                ch_widgets['button'].setStyle(ch_widgets['button'].style())
                ch_widgets['leave_button'].setVisible(ch_name == channel_name)
                
                if ch_name == channel_name:
                    # Önce mevcut kullanıcıları temizle
                    for user_label in list(ch_widgets['users'].values()):
                        ch_widgets['users_layout'].removeWidget(user_label)
                        user_label.deleteLater()
                    ch_widgets['users'].clear()
                    
                    # Kendimizi ekle
                    user_label = QLabel(f"👤 {self.username}")
                    user_label.setStyleSheet("""
                        color: #dcddde;
                        padding: 4px 8px 4px 8px;
                        font-size: 14px;
                    """)
                    ch_widgets['users'][self.username] = user_label
                    ch_widgets['users_layout'].addWidget(user_label)
                    self.current_user_label = user_label
                    
                    # Diğer kullanıcıları ekle
                    if 'users' in response:
                        for username in response['users']:
                            if username != self.username:
                                user_label = QLabel(f"👤 {username}")
                                user_label.setStyleSheet("""
                                    color: #dcddde;
                                    padding: 4px 8px 4px 8px;
                                    font-size: 14px;
                                """)
                                ch_widgets['users'][username] = user_label
                                ch_widgets['users_layout'].addWidget(user_label)
                    
                    ch_widgets['users_container'].show()
                else:
                    ch_widgets['users_container'].hide()
            
            # Chat alanını temizle ve bilgi mesajı göster
            self.chat_area.clear()
            self.chat_area.append(f"<i>{channel_name} kanalına katıldınız.</i>")
            
            # Geçmiş mesajları göster
            if 'history' in response:
                for msg in reversed(response['history']):
                    self.chat_area.append(
                        f"[{msg['timestamp']}] <b>{msg['username']}:</b> {msg['message']}"
                    )
            
            # Ses kaydını başlat
            if not self.is_muted:
                self.audio_manager.start_recording()
            self.audio_manager.start_playback()

    def leave_channel(self, channel_name):
        """Kanaldan ayrıl"""
        if self.socket.current_room == channel_name:
            self.leave_current_channel()
            self.chat_area.append(f"<i>{channel_name} kanalından ayrıldınız.</i>")
            
            # Butonları ve kullanıcı listesini güncelle
            if channel_name in self.channel_widgets:
                ch_widgets = self.channel_widgets[channel_name]
                ch_widgets['button'].setProperty('active', False)
                ch_widgets['button'].setStyle(ch_widgets['button'].style())
                ch_widgets['leave_button'].hide()
                ch_widgets['users_container'].hide()
                
                # Kullanıcı listesini temizle
                for username, user_label in list(ch_widgets['users'].items()):
                    ch_widgets['users_layout'].removeWidget(user_label)
                    user_label.deleteLater()
                    del ch_widgets['users'][username]
                self.current_user_label = None
            
            # Ses kaydını durdur
            self.audio_manager.stop_recording()
            self.audio_manager.stop_playback()
            
            # Mikrofon durumunu güncelle
            self.is_muted = True
            self.mute_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: #40444b;
                    border-radius: 4px;
                }
                QPushButton:checked {
                    background-color: #ed4245;
                    border-radius: 4px;
                }
            """)

    def handle_send_message(self):
        """Mesaj gönderme işlemi"""
        message = self.message_input.toPlainText().strip()
        if message and self.socket.current_room:
            # Mesajı gönder
            self.socket.send_message(message)
            # Mesajı direkt olarak sohbet alanına ekle
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.chat_area.append(f"[{timestamp}] <b>{self.username}:</b> {message}")
            # Input alanını temizle
            self.message_input.clear()

    def handle_message(self, username, message, timestamp):
        """Gelen mesajı sohbet alanına ekle"""
        # Kendi mesajlarımızı tekrar gösterme
        if username != self.username:
            self.chat_area.append(f"[{timestamp}] <b>{username}:</b> {message}")
        # Otomatik olarak en alta kaydır
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def handle_user_joined(self, username, room):
        """Kullanıcı kanala katıldığında"""
        print(f"\n[DEBUG] User joined event - username: {username}, room: {room}")
        print(f"[DEBUG] Current room: {self.socket.current_room}")
        
        if room == self.socket.current_room and username != self.username:
            print(f"[DEBUG] Adding user to channel: {username}")
            self.chat_area.append(f"<i>{username} kanala katıldı</i>")
            
            if room in self.channel_widgets:
                ch_widgets = self.channel_widgets[room]
                if username not in ch_widgets['users']:
                    user_label = QLabel(f"👤 {username}")
                    user_label.setStyleSheet("""
                        color: #dcddde;
                        padding: 4px 8px 4px 8px;
                        font-size: 14px;
                    """)
                    ch_widgets['users'][username] = user_label
                    ch_widgets['users_layout'].addWidget(user_label)
                    ch_widgets['users_container'].show()
                    print(f"[DEBUG] Added user label for: {username}")
                    print(f"[DEBUG] Current users in widget: {list(ch_widgets['users'].keys())}")

    def handle_user_left(self, username, room):
        """Kullanıcı kanaldan ayrıldığında"""
        print(f"User left: {username} from room: {room}")  # Debug için
        if room == self.socket.current_room:
            self.chat_area.append(f"<i>{username} kanaldan ayrıldı</i>")
            # Kullanıcıyı listeden kaldır
            if room in self.channel_widgets:
                ch_widgets = self.channel_widgets[room]
                if username in ch_widgets['users']:
                    user_label = ch_widgets['users'][username]
                    ch_widgets['users_layout'].removeWidget(user_label)
                    user_label.deleteLater()
                    del ch_widgets['users'][username]

    def setup_audio(self):
        """Ses yönetimi için gerekli bağlantıları kur"""
        # Ses verisi hazır olduğunda server'a gönder
        self.audio_manager.audio_data_ready.connect(self.handle_audio_data)
        
        # Başlangıç durumları
        self.is_muted = False  # Mikrofon açık başlar
        self.is_speaker_muted = False  # Hoparlör açık başlar
        
        # Mikrofon butonu
        self.mute_button = QPushButton()
        self.mute_button.setIcon(QIcon("client/assets/mic_off.png"))
        self.mute_button.setIconSize(QSize(24, 24))
        self.mute_button.setFixedSize(40, 40)
        self.mute_button.setToolTip("Mikrofonu Kapat")
        self.mute_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #40444b;
            }
        """)
        self.mute_button.clicked.connect(self.toggle_mute)
        
        # Hoparlör butonu
        self.speaker_button = QPushButton()
        self.speaker_button.setIcon(QIcon("client/assets/speaker_off.png"))
        self.speaker_button.setIconSize(QSize(24, 24))
        self.speaker_button.setFixedSize(40, 40)
        self.speaker_button.setToolTip("Hoparlörü Kapat")
        self.speaker_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #40444b;
            }
        """)
        self.speaker_button.clicked.connect(self.toggle_speaker)
        
        # Ses akışını başlat
        self.audio_manager.start_recording()
        self.audio_manager.start_playback()

    def handle_audio_data(self, audio_data):
        """Mikrofondan gelen ses verisini server'a gönder"""
        if self.socket.current_room:
            self.socket.send_audio(audio_data)
            # Ses iletilirken kullanıcı adını yeşil yap
            if hasattr(self, 'current_user_label') and self.current_user_label:
                self.current_user_label.setStyleSheet("color: #43b581;")  # Yeşil renk
                self.voice_timer.start(100)  # 100ms sonra rengi normale döndür

    def handle_received_audio(self, audio_data):
        """Server'dan gelen ses verisini çal"""
        if self.socket.current_room:
            try:
                # Eğer audio_data bir dictionary ise
                if isinstance(audio_data, dict):
                    sender_sid = audio_data.get('sender_sid')
                    audio = audio_data.get('audio')
                    if sender_sid and sender_sid != self.socket.sio.sid and audio:
                        self.audio_manager.play_audio(audio)
                # Eğer audio_data doğrudan bytes ise
                elif isinstance(audio_data, bytes):
                    # Kendi sesimizi server üzerinden filtreleyeceğiz
                    self.audio_manager.play_audio(audio_data)
            except Exception as e:
                print(f"Ses verisi işleme hatası: {e}")

    def toggle_mute(self):
        """Mikrofon durumunu değiştir"""
        self.is_muted = not self.is_muted
        
        if self.is_muted:
            self.mute_button.setIcon(QIcon("client/assets/mic.png"))
            self.mute_button.setToolTip("Mikrofonu Aç")
            self.audio_manager.stop_recording()
        else:
            self.mute_button.setIcon(QIcon("client/assets/mic_off.png"))
            self.mute_button.setToolTip("Mikrofonu Kapat")
            self.audio_manager.start_recording()

    def toggle_speaker(self):
        """Hoparlör durumunu değiştir"""
        self.is_speaker_muted = not self.is_speaker_muted
        
        if self.is_speaker_muted:
            self.speaker_button.setIcon(QIcon("client/assets/speaker.png"))
            self.speaker_button.setToolTip("Hoparlörü Aç")
            self.audio_manager.stop_playback()
        else:
            self.speaker_button.setIcon(QIcon("client/assets/speaker_off.png"))
            self.speaker_button.setToolTip("Hoparlörü Kapat")
            self.audio_manager.start_playback()

    def toggle_settings_panel(self):
        """Ses ayarları panelini aç/kapat"""
        if self.settings_panel.isVisible():
            self.settings_panel.hide_panel()
        else:
            self.settings_panel.show_panel()

    def closeEvent(self, event):
        """Pencere kapatılırken kaynakları temizle"""
        self.audio_manager.cleanup()
        self.socket.disconnect_from_server()
        super().closeEvent(event)

    def leave_current_channel(self):
        """Mevcut kanaldan ayrıl"""
        if self.socket.current_room:
            current_room = self.socket.current_room
            self.socket.leave_room(current_room)
            
            # Ses kaydını durdur
            self.audio_manager.stop_recording()
            self.audio_manager.stop_playback()
            
            # Kullanıcı listesini güncelle
            if current_room in self.channel_widgets:
                ch_widgets = self.channel_widgets[current_room]
                if 'user_label' in ch_widgets and ch_widgets['user_label']:
                    ch_widgets['user_label'].setParent(None)
                    ch_widgets['user_label'] = None
                self.current_user_label = None

    def reset_voice_indicator(self):
        """Ses iletimi bitince kullanıcı adı rengini normale döndür"""
        if hasattr(self, 'current_user_label') and self.current_user_label:
            self.current_user_label.setStyleSheet("color: #dcddde;")  # Normal renk
        self.voice_timer.stop()

    def eventFilter(self, obj, event):
        """Enter tuşuna basılınca mesaj gönder"""
        if obj == self.message_input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.handle_send_message()
                return True
        return super().eventFilter(obj, event)
