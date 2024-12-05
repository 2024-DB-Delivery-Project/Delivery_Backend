from fastapi import APIRouter
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from app.models.models import User, Address, Order, Product, DeliveryInfo
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.exc import IntegrityError
import random

router = APIRouter(
	prefix="/customers",
    tags=["customers"]
)

class OrderCreate(BaseModel):
    customer_id : int
    product_id: int

class BoughtList(BaseModel):
    name: str
    phone_number: str

class GetDeliveryStatus(BaseModel):
    customer_id : int


@router.get("/product_list")
def get_product(db: Session = Depends(get_db)):
    try:
        products = db.query(Product).all()
        if not products:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
        # JSON 형식으로 데이터를 묶어서 반환
        product_list = [
            {
                "product_id": product.product_id,
                "name": product.name,
                "description": product.description,
                "price": product.price
            }
            for product in products
        ]
        return {"products": product_list}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/buy")
def buy_product(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        # 고객 정보 조회
        customer = db.query(User).filter(User.user_id == order.customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        # 제품 정보 조회
        product = db.query(Product).filter(Product.product_id == order.product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # 주소 ID가 없는 유저에 대한 처리
        if not customer.address_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found for this user")

        # 주문 생성
        new_order = Order(
            customer_id=order.customer_id,
            product_id=order.product_id,
            address_id=customer.address_id  # address_id만 저장 (외래 키로)
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        # DeliveryInfo 생성
        while True:
            tracking_number = random.randint(100000, 999999)  # 6자리 랜덤 숫자 생성
            existing_tracking = db.query(DeliveryInfo).filter(DeliveryInfo.tracking_number == tracking_number).first()
            if not existing_tracking:
                break
 
        new_delivery = DeliveryInfo(
            order_id=new_order.order_id,
            tracking_number=tracking_number,
            delivery_status="ready",
            delivery_address=new_order.address_id,  # Order의 address_id 사용
            driver_id=None,  # 빈 값
            logistic_id=None  # 빈 값
        )
        db.add(new_delivery)
        db.commit()
        db.refresh(new_delivery)

        return {
            "msg": "Order created successfully",
            "order_id": new_order.order_id
        }

    except Exception as e:
    # 상세 예외 메시지 출력
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.post("/bought_list")
def get_bought_list(bought: BoughtList, db: Session = Depends(get_db)):
    try:
        # Step 1: name과 phone_number를 이용해 User 테이블에서 user_id 조회
        customer = db.query(User).filter(
            User.name == bought.name,
            User.phone_number == bought.phone_number
        ).first()
        
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        
        # Step 2: user_id를 기준으로 Order 테이블에서 해당 고객의 주문 조회
        orders = db.query(Order).filter(Order.customer_id == customer.user_id).all()
        
        if not orders:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No orders found for this customer")
        
        # Step 3: 각 주문에 대해 product_id와 address_id를 사용하여 관련 정보 조회
        order_list = []
        for order in orders:
            # Product 정보 조회
            product = db.query(Product).filter(Product.product_id == order.product_id).first()
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found for product_id {order.product_id}")
            
            # Address 정보 조회
            address = db.query(Address).filter(Address.address_id == order.address_id).first()
            if not address:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Address not found for address_id {order.address_id}")
            
            # 주문 정보에 추가
            order_list.append({
                "order_id": order.order_id,
                "product_name": product.name,
                "product_price": product.price,
                "customer_name": customer.name,
                "customer_phone_number": customer.phone_number,
                "city": address.city,
                "town": address.town,
                "village": address.village
            })
        
        return {"orders": order_list}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/delivery_status")
def get_delivery_status(status: GetDeliveryStatus, db: Session = Depends(get_db)):
    try:
        # Order에서 customer_id에 해당하는 주문 ID 조회
        orders = db.query(Order.order_id).filter(Order.customer_id == status.customer_id).all()
        if not orders:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No orders found for this customer")

        # 주문 ID를 통해 deliveryinfo의 delivery_status 조회
        order_ids = [order.order_id for order in orders]
        delivery_statuses = db.query(DeliveryInfo.order_id, DeliveryInfo.delivery_status).filter(
            DeliveryInfo.order_id.in_(order_ids)
        ).all()

        if not delivery_statuses:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No delivery info found for these orders")

        # 결과 반환
        return {
            "customer_id": status.customer_id,
            "delivery_statuses": [
                {"order_id": status.order_id, "delivery_status": status.delivery_status}
                for status in delivery_statuses
            ],
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")