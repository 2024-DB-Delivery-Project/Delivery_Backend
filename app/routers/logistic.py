from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth.auth import get_current_user
from app.database import get_db
from app.models.models import Address, DeliveryInfo, DriverDeliveryInfo, Order, User
from collections import defaultdict
from sqlalchemy.orm import joinedload


router = APIRouter(
	prefix="/logistic",
    tags=["logistic"]
)

class AssignDriverRequest(BaseModel):
    delivery_id: int
    driver_id: int


@router.get("/deliveries")
def get_deliveries_for_logistic(db: Session = Depends(get_db), logistic_id: int = Depends(get_current_user)):
    try:
        # logistic_id로 배송 정보 조회
        deliveries = (
            db.query(DeliveryInfo)
            .options(
                joinedload(DeliveryInfo.info_address),   # Address 조인
                joinedload(DeliveryInfo.info_order).joinedload(Order.order_product),  # Product 조인
                joinedload(DeliveryInfo.info_order).joinedload(Order.order_customer)  # Customer 조인
            )
            .filter(DeliveryInfo.logistic_id == logistic_id)
            .all()
        )

        if not deliveries:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No deliveries found for this logistic")

        # city를 기준으로 그룹화
        grouped_deliveries = defaultdict(list)
        for delivery in deliveries:
            # Address 정보
            city = delivery.info_address.city if delivery.info_address else "Unknown City"
            detailed_address = f"{delivery.info_address.town}, {delivery.info_address.village}" if delivery.info_address else "Unknown Address"

            # Order, Product, Customer 정보
            product_name = delivery.info_order.order_product.name if delivery.info_order and delivery.info_order.order_product else "Unknown Product"
            customer_name = delivery.info_order.order_customer.name if delivery.info_order and delivery.info_order.order_customer else "Unknown Customer"
            customer_phone = delivery.info_order.order_customer.phone_number if delivery.info_order and delivery.info_order.order_customer else "Unknown Phone"

            # 배송 정보 그룹화
            grouped_deliveries[city].append({
                "delivery_id": delivery.delivery_id,
                "order_id": delivery.order_id,
                "tracking_number": delivery.tracking_number,
                "delivery_status": delivery.delivery_status,
                "product_name": product_name,
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "detailed_address": detailed_address,
            })
        # 응답 구성
        response = [
            {
                "city": city,
                "deliveries": deliveries
            }
            for city, deliveries in grouped_deliveries.items()
        ]
        return {"logistic_id": logistic_id, "grouped_deliveries": response}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/by_city")
def get_drivers_by_city(city: str, db: Session = Depends(get_db)):
    try:
        # 'DRIVER' 역할의 사용자 중, 특정 city를 가진 사용자 조회
        drivers = (
            db.query(User)
            .join(Address, User.address_id == Address.address_id)
            .filter(User.role == "DRIVER", Address.city == city)
            .all()
        )

        if not drivers:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No drivers found for the specified city")

        # JSON 응답 구성
        response = [
            {
                "user_id": driver.user_id,
                "name": driver.name,
                "phone_number": driver.phone_number,
                "city": city
            }
            for driver in drivers
        ]
        return {"city": city, "drivers": response}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/assign_driver")
def assign_driver(request: AssignDriverRequest, db: Session = Depends(get_db)):
    try:
        # 1. delivery_id로 DeliveryInfo 조회
        delivery = db.query(DeliveryInfo).filter(DeliveryInfo.delivery_id == request.delivery_id).first()
        if not delivery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")

        # 2. driver_id로 Driver 조회 및 검증
        driver = db.query(User).filter(User.user_id == request.driver_id, User.role == "DRIVER").first()
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found or invalid role")

        # 3. DeliveryInfo 업데이트
        delivery.driver_id = request.driver_id
        delivery.delivery_status = "Shipped"

        driver_delivery = DriverDeliveryInfo(
            delivery_id=request.delivery_id,
            driver_id=request.driver_id
        )
        db.add(driver_delivery)

        # 4. 변경 사항 커밋
        db.commit()
        db.refresh(delivery)

        # 성공 응답 반환
        return {
            "msg": "Driver assigned successfully",
            "delivery_id": delivery.delivery_id,
            "driver_id": delivery.driver_id,
            "delivery_status": delivery.delivery_status
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")