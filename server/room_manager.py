class RoomManager:
    def __init__(self):
        self.rooms = {
            'Genel Sohbet': set(),
            'Oyun Odası': set(),
            'Müzik Odası': set()
        }
    
    def add_user_to_room(self, room_name, user_sid):
        """Kullanıcıyı odaya ekle"""
        if room_name in self.rooms:
            self.rooms[room_name].add(user_sid)
            return True
        return False
    
    def remove_user_from_room(self, room_name, user_sid):
        """Kullanıcıyı odadan çıkar"""
        if room_name in self.rooms:
            self.rooms[room_name].discard(user_sid)
            return True
        return False
    
    def remove_user_from_all_rooms(self, user_sid):
        """Kullanıcıyı tüm odalardan çıkar"""
        for room in self.rooms.values():
            room.discard(user_sid)
    
    def get_room_users(self, room_name):
        """Odadaki kullanıcıları getir"""
        return list(self.rooms.get(room_name, set()))
    
    def get_user_room(self, user_sid):
        """Kullanıcının bulunduğu odayı bul"""
        for room_name, users in self.rooms.items():
            if user_sid in users:
                return room_name
        return None
    
    def room_exists(self, room_name):
        """Oda var mı kontrol et"""
        return room_name in self.rooms
