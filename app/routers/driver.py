from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.models import DriverDeliveryInfo, DeliveryInfo
from app.auth.auth import get_current_user


router = APIRouter(
	prefix="/driver",
    tags=["driver"]
)

class UpdateDeliveryStatusRequest(BaseModel):
    delivery_id: int

@router.get("/deliveries")
def get_driver_deliveries(db: Session = Depends(get_db), driver_id: int = Depends(get_current_user)):
    try:
        # driver_id로 driverdeliveryinfo 조회
        driver_deliveries = (
            db.query(DriverDeliveryInfo)
            .options(joinedload(DriverDeliveryInfo.driver_interface))  # DeliveryInfo와 조인
            .filter(DriverDeliveryInfo.driver_id == driver_id)
            .all()
        )

        if not driver_deliveries:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No deliveries found for this driver")

        # 응답 데이터 구성
        response = []
        for driver_delivery in driver_deliveries:
            delivery = driver_delivery.driver_interface

            # 배송 정보가 없는 경우 무시
            if not delivery:
                continue

            # Address 정보
            address = delivery.info_address
            detailed_address = f"{address.city}, {address.town}, {address.village}" if address else "Unknown Address"

            # Product 정보
            product = delivery.info_order.order_product if delivery.info_order else None
            product_name = product.name if product else "Unknown Product"

            # Customer 정보
            customer = delivery.info_order.order_customer if delivery.info_order else None
            customer_name = customer.name if customer else "Unknown Customer"
            customer_phone = customer.phone_number if customer else "Unknown Phone"

            # 응답 데이터 추가
            response.append({
                "delivery_id": delivery.delivery_id,
                "order_id": delivery.order_id,
                "tracking_number": delivery.tracking_number,
                "delivery_status": delivery.delivery_status,
                "product_name": product_name,
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "detailed_address": detailed_address
            })

        return {"driver_id": driver_id, "deliveries": response}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/mark_delivered")
def mark_delivered(request: UpdateDeliveryStatusRequest, db: Session = Depends(get_db)):
    try:
        # 1. delivery_id로 DeliveryInfo 조회
        delivery = db.query(DeliveryInfo).filter(DeliveryInfo.delivery_id == request.delivery_id).first()
        if not delivery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")

        # 2. delivery_status를 Delivered로 업데이트
        delivery.delivery_status = "Delivered"

        # 3. driverdeliveryinfo에서 해당 delivery_id 삭제
        driver_delivery = db.query(DriverDeliveryInfo).filter(DriverDeliveryInfo.delivery_id == request.delivery_id).first()
        if driver_delivery:
            db.delete(driver_delivery)

        # 4. 변경 사항 커밋
        db.commit()
        db.refresh(delivery)

        # 성공 응답 반환
        return {
            "msg": "Delivery marked as delivered and driver record removed",
            "delivery_id": delivery.delivery_id,
            "delivery_status": delivery.delivery_status
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")