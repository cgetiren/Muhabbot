from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Room(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    messages = relationship("Message", back_populates="room")
    
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    username = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    
    room = relationship("Room", back_populates="messages")
    
class Database:
    def __init__(self, db_url="sqlite:///chat.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Varsayılan odaları oluştur
        self._create_default_rooms()
        
    def _create_default_rooms(self):
        default_rooms = ["Genel Sohbet", "Oyun Odası", "Müzik Odası"]
        
        for room_name in default_rooms:
            if not self.session.query(Room).filter_by(name=room_name).first():
                room = Room(name=room_name)
                self.session.add(room)
        
        self.session.commit()
        
    def add_message(self, room_name, username, content):
        """Yeni mesaj ekle"""
        room = self.session.query(Room).filter_by(name=room_name).first()
        if room:
            message = Message(
                room_id=room.id,
                username=username,
                content=content
            )
            self.session.add(message)
            self.session.commit()
            return message
        return None
        
    def get_room_messages(self, room_name, limit=50):
        """Odadaki son mesajları getir"""
        room = self.session.query(Room).filter_by(name=room_name).first()
        if room:
            return (self.session.query(Message)
                   .filter_by(room_id=room.id)
                   .order_by(Message.timestamp.desc())
                   .limit(limit)
                   .all())
        return []
        
    def get_rooms(self):
        """Tüm odaları getir"""
        return self.session.query(Room).all()
