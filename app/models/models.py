from sqlalchemy import Integer, String, TIMESTAMP, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp
from ..database import Base

# Address 테이블 정의
class Address(Base):
    __tablename__ = 'address'  # 테이블 이름 수정
    address_id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False)
    town = Column(String, nullable=False)
    village = Column(String, nullable=False)

    users = relationship("User", back_populates="user_address")  # User와의 관계 설정

# User 테이블 정의
class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String(15), nullable=False)
    address_id = Column(Integer, ForeignKey("address.address_id"), nullable=False)  # 테이블 이름 수정
    role = Column(String, nullable=False)
    login_id = Column(String, nullable=False)
    password = Column(String, nullable=False)

    user_address = relationship("Address", back_populates="users")  # Address와의 관계 설정



