import os
from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, create_engine, Session, Relationship, Column, JSON

# Database Configuration
DATABASE_URL = "sqlite:///./finwise.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Models
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    financial_data: List["FinancialData"] = Relationship(back_populates="user")
    uploaded_files: List["UploadedFile"] = Relationship(back_populates="user")
    chat_history: List["ChatHistory"] = Relationship(back_populates="user")

class FinancialData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    income: float
    expenses: float
    savings: float
    debts: float = Field(default=0.0)
    categories: Dict[str, float] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="financial_data")

class UploadedFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    file_name: str
    extracted_data: Dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="uploaded_files")

class ChatHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    message: str
    response: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="chat_history")

# Database initialization
def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
