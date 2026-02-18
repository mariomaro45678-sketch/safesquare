from sqlalchemy import Column, Integer, String, Boolean
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """User accounts (for future authentication)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User {self.email}>"
