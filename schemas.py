from sqlalchemy import create_engine, Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    team_id = Column(String, primary_key=True)
    display_name = Column(String)
    channels = relationship("Channel", back_populates="team")

class Channel(Base):
    __tablename__ = 'channels'
    channel_id = Column(String, primary_key=True)
    display_name = Column(String)
    team_id = Column(String, ForeignKey('teams.team_id'))
    team = relationship("Team", back_populates="channels")
    messages = relationship("Message", back_populates="channel")

class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(String, primary_key=True)
    content = Column(String)
    channel_id = Column(String, ForeignKey('channels.channel_id'))
    channel = relationship("Channel", back_populates="messages")
    replies = relationship("Reply", back_populates="message")

class Reply(Base):
    __tablename__ = 'replies'
    reply_id = Column(String, primary_key=True)
    content = Column(String)
    message_id = Column(String, ForeignKey('messages.message_id'))
    message = relationship("Message", back_populates="replies")

# Création de la base de données
engine = create_engine('sqlite:///teams_data.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()