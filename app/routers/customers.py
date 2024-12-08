from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.auth import get_current_user
from ..database import get_db
from app.models.models import User, Address, Order, Product, DeliveryInfo
from pydantic import BaseModel


router = APIRouter(
	prefix="/customers",
    tags=["customers"]
)

class BoughtList(BaseModel):
    name: str
    phone_number: str


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


@router.get("/purchased_products")
def get_purchased_products(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    try:
        # 1. Order 테이블에서 user_id로 주문된 product_id 조회
        orders = db.query(Order.product_id).filter(Order.customer_id == user_id).all()
        
        # 주문이 없을 경우 빈 리스트 반환
        if not orders:
            return {"user_id": user_id, "purchased_products": []}
        
        # 2. product_id만 리스트로 추출
        product_ids = [order.product_id for order in orders]

        # 3. Product 테이블에서 product_id로 관련 상품 정보 조회
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()

        # 4. 응답 데이터 구성
        response = [
            {
                "product_id": product.product_id,
                "name": product.name,
                "description": product.description,
                "price": product.price
            }
            for product in products
        ]

        return {"user_id": user_id, "purchased_products": response}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/buy")
def buy_product(product_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    try:
        # 고객 정보 조회 (user_id 확인)
        customer = db.query(User).filter(User.user_id == user_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

        # 제품 정보 조회
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # 주소 ID가 없는 유저에 대한 처리
        if not customer.address_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has no address")

        # 주문 생성
        new_order = Order(
            customer_id=user_id,
            product_id=product_id,
            address_id=customer.address_id
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        # DeliveryInfo 생성
        new_delivery = DeliveryInfo(
            order_id=new_order.order_id,
            tracking_number=None,
            delivery_status="Received",
            delivery_address=new_order.address_id,
            driver_id=None,
            logistic_id=None
        )
        db.add(new_delivery)
        db.commit()
        db.refresh(new_delivery)

        return {
            "msg": "Order created successfully",
            "order_id": new_order.order_id
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
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


@router.get("/delivery_status")
def get_delivery_status(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    try:
        # Order에서 user_id에 해당하는 주문 ID 조회
        orders = db.query(Order.order_id).filter(Order.customer_id == user_id).all()
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
            "user_id": user_id,
            "delivery_statuses": [
                {"order_id": status.order_id, "delivery_status": status.delivery_status}
                for status in delivery_statuses
            ],
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")