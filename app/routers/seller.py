from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
import random

from app.auth.auth import get_current_user
from ..database import get_db
from app.models.models import Order, Product, DeliveryInfo
from fastapi import Depends, HTTPException, status

router = APIRouter(
	prefix="/seller",
    tags=["seller"]
)

class SelectLogisticRequest(BaseModel):
    order_id: int

class TrackingNumberRequest(BaseModel):
    tracking_number: int


@router.get("/orders")
def get_seller_orders(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    try:
        # 1. 해당 사용자가 등록한 제품 조회
        products = db.query(Product).filter(Product.user_id == user_id).all()
        if not products:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found for this user")

        # 2. 등록된 제품의 product_id로 관련 주문 조회
        product_ids = [product.product_id for product in products]
        orders = db.query(Order).filter(Order.product_id.in_(product_ids)).all()

        if not orders:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No orders found for this seller's products")

        # 3. JSON 형식으로 데이터 구성
        response = [
            {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "logistic_id": order.logistic_id,
                "address_id": order.address_id,
                "product": {
                    "product_id": product.product_id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price
                }
            }
            for order in orders
            for product in products if product.product_id == order.product_id
        ]
        return {"seller_id": user_id, "orders": response}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def generate_unique_tracking_number(db: Session) -> int:
    while True:
        tracking_number = random.randint(100000, 999999)  # 6자리 난수 생성
        existing_tracking = db.query(DeliveryInfo).filter(DeliveryInfo.tracking_number == tracking_number).first()
        if not existing_tracking:
            return tracking_number

@router.post("/select_logistic")
def select_logistic(request: SelectLogisticRequest, db: Session = Depends(get_db)):
    try:
        # deliveryinfo에서 order_id로 해당 데이터 조회
        delivery = db.query(DeliveryInfo).filter(DeliveryInfo.order_id == request.order_id).first()
        if not delivery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found in delivery info")

        # Order 테이블에서 order_id로 해당 데이터 조회
        order = db.query(Order).filter(Order.order_id == request.order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found in order table")

        # logistic_id와 delivery_status 업데이트
        delivery.logistic_id = 15  # 임의의 값 지정
        delivery.delivery_status = "Processing"

        # Order 테이블의 logistic_id 업데이트
        order.logistic_id = delivery.logistic_id

        # tracking_number가 없을 경우 새로 생성
        if not delivery.tracking_number:
            delivery.tracking_number = generate_unique_tracking_number(db)

        # 데이터베이스에 변경 사항 적용
        db.commit()
        db.refresh(delivery)
        db.refresh(order)

        # 성공 응답 반환
        return {
            "msg": "Logistic updated successfully",
            "order_id": request.order_id,
            "logistic_id": delivery.logistic_id,
            "delivery_status": delivery.delivery_status,
            "tracking_number": delivery.tracking_number
        }

    except HTTPException as http_exc: 
        raise http_exc  # HTTPException은 그대로 반환
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/get_delivery_status")
def get_delivery_status(request: TrackingNumberRequest, db: Session = Depends(get_db)):
    try:
        # DeliveryInfo에서 tracking_number로 데이터 조회
        delivery_info = db.query(DeliveryInfo).filter(DeliveryInfo.tracking_number == request.tracking_number).first()
        
        if not delivery_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No delivery found for tracking number {request.tracking_number}"
            )

        # 배송 상태 반환
        return {
            "tracking_number": delivery_info.tracking_number,
            "delivery_status": delivery_info.delivery_status
        }

    except HTTPException as http_exc:
        raise http_exc  # HTTPException을 그대로 반환
    except Exception as e:
        print(f"Unhandled exception: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")