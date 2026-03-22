from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from typing import List, Dict
from src.config import settings

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), index=True)
    role = Column(String(50)) # 'user' or 'model'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

if settings.database_url.startswith("sqlite"):
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.database_url)
    
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_message(user_id: str, role: str, content: str):
    db = SessionLocal()
    try:
        msg = Message(user_id=user_id, role=role, content=content)
        db.add(msg)
        db.commit()
    finally:
        db.close()

def get_history(user_id: str, limit: int = 15) -> List[Dict[str, str]]:
    db = SessionLocal()
    try:
        messages = db.query(Message).filter(Message.user_id == user_id).order_by(Message.timestamp.desc()).limit(limit).all()
        # Return in chronological order
        return [{"role": m.role, "parts": [m.content]} for m in reversed(messages)]
    finally:
        db.close()
