from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

# Address 테이블 정의
class Address(Base):
    __tablename__ = 'address'

    address_id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False)
    town = Column(String, nullable=False)
    village = Column(String, nullable=False)

    address_user = relationship("User", back_populates="user_address")  # User와의 관계 설정
    address_order = relationship("Order", back_populates="order_address")  # Order와의 관계 설정
    address_info = relationship("DeliveryInfo", back_populates="info_address")

# User 테이블 정의
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String(15), nullable=False)
    role = Column(String, nullable=False)
    address_id = Column(Integer, ForeignKey("address.address_id"), nullable=False)  # 테이블 이름 수정
    login_id = Column(String, nullable=False)
    password = Column(String, nullable=False)

    user_address = relationship("Address", foreign_keys=[address_id], back_populates="address_user")  # Address와의 관계 설정
    
    customer_order = relationship("Order", foreign_keys="Order.customer_id", back_populates="order_customer")
    logistic_order = relationship("Order", foreign_keys="Order.logistic_id", back_populates="order_logistic")
    user_product = relationship("Product", back_populates="product_user")  # Product와의 관계 설정

    user_infodriver = relationship("DeliveryInfo", foreign_keys="DeliveryInfo.driver_id", back_populates="infodriver_user")
    user_infologistic = relationship("DeliveryInfo", foreign_keys="DeliveryInfo.logistic_id", back_populates="infologistic_user")
    user_driver = relationship("DriverDeliveryInfo", back_populates="driver_user")

# Order 테이블 정의
class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    logistic_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    address_id = Column(Integer, ForeignKey("address.address_id"), nullable=False)  # 주소 ID로 수정

    order_customer = relationship("User", foreign_keys=[customer_id], back_populates="customer_order")
    order_logistic = relationship("User", foreign_keys=[logistic_id], back_populates="logistic_order")
    order_product = relationship("Product", foreign_keys=[product_id], back_populates="product_order")
    order_address = relationship("Address", foreign_keys=[address_id], back_populates="address_order")  # Address와의 관계 설정
    order_info = relationship("DeliveryInfo", back_populates="info_order")

# Product 테이블 정의
class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    product_user = relationship("User", foreign_keys=[user_id], back_populates="user_product")  # User와의 관계 설정
    product_order = relationship("Order", back_populates="order_product")

class DeliveryInfo(Base):
    __tablename__ = 'deliveryinfo'

    delivery_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.user_id"))
    logistic_id = Column(Integer, ForeignKey("users.user_id"))
    tracking_number = Column(String, nullable=False)
    delivery_status = Column(String, nullable=False)
    delivery_address = Column(Integer, ForeignKey("address.address_id"), nullable=False)

    info_order = relationship("Order", foreign_keys=[order_id], back_populates="order_info")
    infodriver_user = relationship("User", foreign_keys=[driver_id], back_populates="user_infodriver")
    infologistic_user = relationship("User", foreign_keys=[logistic_id], back_populates="user_infologistic")
    info_address = relationship("Address", foreign_keys=[delivery_address], back_populates="address_info")

    interface_driver = relationship("DriverDeliveryInfo", back_populates="driver_interface")


class DriverDeliveryInfo(Base):
    __tablename__ = "driverdeliveryinfo"

    driver_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    delivery_id = Column(Integer, ForeignKey("deliveryinfo.delivery_id"), nullable=False)
    id = Column(Integer, primary_key=True, index=True)

    driver_user = relationship("User", foreign_keys=[driver_id], back_populates="user_driver")
    driver_interface = relationship("DeliveryInfo", foreign_keys=[delivery_id], back_populates="interface_driver")