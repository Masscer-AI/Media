# database.py
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Float,
    Boolean,
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from databases import Database
from datetime import datetime, timedelta

DATABASE_URL = "sqlite:///./test.db"

database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    messages = relationship("Message", back_populates="conversation")
    user = relationship("User", back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender = Column(String, nullable=False)  # 'user' or 'assistant'
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="messages")


class Audio(Base):
    __tablename__ = "audios"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    transcription = Column(Text, nullable=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    organizations = relationship("Organization", back_populates="owner")
    model_settings = relationship("ModelSetting", back_populates="user")
    conversations = relationship(
        "Conversation", back_populates="user"
    )  # New relationship


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="organizations")
    config = relationship(
        "OrganizationConfig", uselist=False, back_populates="organization"
    )
    billing_ratio = Column(Float, default=1.20)  # New field
    consumption_periods = relationship(
        "ConsumptionPeriod", back_populates="organization"
    )  # New relationship


class OrganizationConfig(Base):
    __tablename__ = "organization_configs"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    OPENAI_API_KEY = Column(String, nullable=False)
    organization = relationship("Organization", back_populates="config")


class ModelSetting(Base):
    __tablename__ = "model_settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    setting_name = Column(String, nullable=False)
    setting_value = Column(Text, nullable=False)
    user = relationship("User", back_populates="model_settings")


class ConsumptionPeriod(Base):
    __tablename__ = "consumption_periods"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="OPEN")  # OPEN, BILLED
    organization = relationship("Organization", back_populates="consumption_periods")
    consumption_items = relationship(
        "ConsumptionItem", back_populates="consumption_period"
    )


class ConsumptionItem(Base):
    __tablename__ = "consumption_items"
    id = Column(Integer, primary_key=True, index=True)
    consumption_period_id = Column(
        Integer, ForeignKey("consumption_periods.id"), nullable=False
    )
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    consumption_period = relationship(
        "ConsumptionPeriod", back_populates="consumption_items"
    )


class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    is_permanent = Column(Boolean, default=False)
    expiration_date = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="tokens")

    def __init__(self, user_id, token, is_permanent=False):
        self.user_id = user_id
        self.token = token
        self.is_permanent = is_permanent
        if not is_permanent:
            self.expiration_date = datetime.utcnow() + timedelta(days=3)


User.tokens = relationship("Token", back_populates="user")


Base.metadata.create_all(bind=engine)
