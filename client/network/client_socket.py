import socketio
from PyQt6.QtCore import QObject, pyqtSignal

class ClientSocket(QObject):
    # Sinyaller
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    message_received = pyqtSignal(str, str, str)  # username, message, timestamp
    user_joined = pyqtSignal(str, str)  # username, room
    user_left = pyqtSignal(str, str)    # username, room
    audio_received = pyqtSignal(bytes)  # Yeni sinyal
    
    def __init__(self):
        super().__init__()
        self.sio = socketio.Client()
        self.setup_events()
        self.current_room = None
        
    def setup_events(self):
        @self.sio.event
        def connect():
            print("Server'a bağlandı")
            self.connected.emit()
            
        @self.sio.event
        def disconnect():
            print("Server bağlantısı kesildi")
            self.disconnected.emit()
            
        @self.sio.on('new_message')
        def on_message(data):
            print(f"Mesaj alındı: {data}")  # Debug
            self.message_received.emit(
                data['username'],
                data['message'],
                data['timestamp']
            )
            
        @self.sio.on('user_joined')
        def on_user_joined(data):
            print(f"Kullanıcı katıldı: {data}")  # Debug
            self.user_joined.emit(data['username'], data['room'])
            
        @self.sio.on('user_left')
        def on_user_left(data):
            print(f"Kullanıcı ayrıldı: {data}")  # Debug
            self.user_left.emit(data['username'], data['room'])
        
        @self.sio.on('audio_data')
        def on_audio_data(data):
            self.audio_received.emit(data['audio'])
    
    def connect_to_server(self, url='http://129.159.223.71:8080'):
        try:
            self.sio.connect(url)
            return True
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            return False
            
    def login(self, username):
        return self.sio.call('login', username)
        
    def join_room(self, room_name):
        """Odaya katıl ve yanıtı bekle"""
        try:
            print(f"Odaya katılma isteği gönderiliyor: {room_name}")  # Debug için
            response = self.sio.call('join_room', room_name)
            print(f"Server yanıtı: {response}")  # Debug için
            
            if response and response.get('status') == 'success':
                self.current_room = room_name
                print(f"Başarıyla katıldı: {room_name}")  # Debug için
            return response
        except Exception as e:
            print(f"Odaya katılma hatası: {e}")  # Debug için
            return {'status': 'error', 'message': str(e)}
        
    def leave_room(self, room_name):
        if self.current_room:
            self.sio.emit('leave_room', room_name)
            self.current_room = None
            
    def send_message(self, message):
        """Mesaj gönder"""
        if self.current_room:
            print(f"Mesaj gönderiliyor: {message} to {self.current_room}")  # Debug
            self.sio.emit('send_message', {
                'room': self.current_room,
                'message': message
            })
            
    def disconnect_from_server(self):
        if self.sio.connected:
            self.sio.disconnect()

    def send_audio(self, audio_data):
        """Ses verisini server'a gönder"""
        if self.current_room:
            self.sio.emit('audio_data', {
                'room': self.current_room,
                'audio': audio_data
            })
