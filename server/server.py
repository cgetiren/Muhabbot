import socketio
from aiohttp import web
from datetime import datetime
from .database import Database

class VoiceChatServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
        self.app = web.Application()
        self.sio.attach(self.app)
        
        # Test endpoint'i ekle
        self.app.router.add_get('/', self.handle_index)
        
        self.users = {}  # {sid: username}
        self.rooms = {
            'Genel Sohbet': set(),
            'Oyun Odası': set(),
            'Müzik Odası': set()
        }
        self.db = Database()
        self.setup_events()
        
    def setup_events(self):
        @self.sio.event
        async def connect(sid, environ):
            print(f'Client bağlandı: {sid}')
            
        @self.sio.event
        async def disconnect(sid):
            if sid in self.users:
                username = self.users[sid]
                # Kullanıcıyı tüm odalardan çıkar
                for room_name, users in self.rooms.items():
                    if sid in users:
                        users.discard(sid)
                        await self.sio.emit('user_left', {
                            'username': username,
                            'room': room_name
                        }, room=room_name)
                del self.users[sid]
                print(f'Client ayrıldı: {username} ({sid})')
                
        @self.sio.event
        async def login(sid, username):
            self.users[sid] = username
            print(f'Kullanıcı girişi: {username} ({sid})')
            return {'status': 'success'}
            
        @self.sio.event
        async def join_room(sid, room_name):
            print(f"Join room isteği: {room_name} from {sid}")
            if room_name in self.rooms:
                username = self.users[sid]
                print(f"Kullanıcı bulundu: {username}")
                
                # Önce diğer odalardan çık
                for old_room, users in self.rooms.items():
                    if sid in users:
                        users.discard(sid)
                        await self.sio.emit('user_left', {
                            'username': username,
                            'room': old_room
                        }, room=old_room)
                        self.sio.leave_room(sid, old_room)  # Eski odadan çık
                
                # Yeni odaya katıl
                self.sio.enter_room(sid, room_name)  # await kaldırıldı
                self.rooms[room_name].add(sid)
                
                # Odadaki kullanıcı listesini hazırla
                room_users = [self.users[user_sid] for user_sid in self.rooms[room_name]]
                
                # Odadaki diğer kullanıcılara haber ver
                await self.sio.emit('user_joined', {
                    'username': username,
                    'room': room_name
                }, room=room_name)
                
                print(f'{username} odaya katıldı: {room_name}')
                print(f'Odadaki kullanıcılar: {room_users}')
                
                return {
                    'status': 'success',
                    'users': room_users  # Kullanıcı listesini gönder
                }
            
            print(f"Oda bulunamadı: {room_name}")
            return {'status': 'error', 'message': 'Oda bulunamadı'}
            
        @self.sio.event
        async def leave_room(sid, room_name):
            if room_name in self.rooms and sid in self.rooms[room_name]:
                username = self.users[sid]
                self.rooms[room_name].discard(sid)
                
                # Odadaki diğer kullanıcılara haber ver
                await self.sio.emit('user_left', {
                    'username': username,
                    'room': room_name
                }, room=room_name)
                
                return {'status': 'success'}
            return {'status': 'error', 'message': 'Oda veya kullanıcı bulunamadı'}
            
        @self.sio.event
        async def audio_data(sid, data):
            room_name = data['room']
            if room_name in self.rooms and sid in self.rooms[room_name]:
                for user_sid in self.rooms[room_name]:
                    if user_sid != sid:  # Kendisine gönderme
                        await self.sio.emit('audio_data', {
                            'audio': data['audio'],
                            'sender_sid': sid  # Gönderen kişinin ID'sini ekle
                        }, room=user_sid)
                
        @self.sio.event
        async def send_message(sid, data):
            """Mesaj gönderme olayı"""
            if sid in self.users and data.get('room') in self.rooms:
                username = self.users[sid]
                room = data['room']
                message = data['message']
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Mesajı veritabanına kaydet
                self.db.add_message(room, username, message)
                
                # Odadaki herkese mesajı gönder
                await self.sio.emit('new_message', {
                    'username': username,
                    'message': message,
                    'timestamp': timestamp
                }, room=room)
        
    async def start(self, host='0.0.0.0', port=8080):
        print(f'Server başlatılıyor... {host}:{port}')
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
    async def handle_index(self, request):
        """Test için basit bir endpoint"""
        return web.Response(text="Voice Chat Server is running!", status=200)

if __name__ == '__main__':
    import asyncio
    import sys
    
    async def main():
        server = VoiceChatServer()
        await server.start()
        try:
            # Server'ı sürekli çalışır durumda tut
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Server kapatılıyor...")
            sys.exit(0)
    
    asyncio.run(main())
