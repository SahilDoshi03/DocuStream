from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, Text, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from pgvector.sqlalchemy import Vector


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/docustream")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    metadata_ = Column("metadata", JSON, default={})
    embedding = Column(Vector(384))

class Chat(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.now)
    
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    files = relationship("File", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    chat_id = Column(String, ForeignKey("chats.id"))
    role = Column(String) # user, assistant
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    # Store message parts or other metadata if needed
    meta = Column(JSON, default={})

    chat = relationship("Chat", back_populates="messages")

class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True)
    chat_id = Column(String, ForeignKey("chats.id"), nullable=True) # Can be null if uploaded before chat created? Or usually linked.
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.now)
    
    chat = relationship("Chat", back_populates="files")

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
