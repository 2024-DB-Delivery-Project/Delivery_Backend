from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from app.models.models import User, Address
from pydantic import BaseModel

app = FastAPI()

# Pydantic 모델 정의 (회원가입 요청 데이터 검증)
class AddressCreate(BaseModel):
    city: str
    town: str
    village: str

class UserCreate(BaseModel):
    name: str
    phone_number: str
    role: str
    address_id: int

# 회원가입 API 
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    
    try:
        # user_id = db.query(User.user_id).filter_by(
        #     name=user.name, phone_number=user.phone_number, role=user.role, address=user.address
        #     ).scalar()
        
        # if user_id:
        #     return {
        #         "msg": "User already exists",
        #         "user_id": user_id,
        #     }
        address = db.query(Address).filter(Address.address_id == user.address_id).first()
        if not address:
            raise HTTPException(status_code=400, detail="Invalid address_id")

        # 존재하지 않는 경우 새로 추가 
        new_user = User(
            name=user.name, 
            phone_number=user.phone_number, 
            role=user.role,
            address_id=user.address_id
            )
        db.add(new_user) 
        db.commit()
        db.refresh(new_user)

        return {
            "msg": "User created successfully",
            "user_id": new_user.user_id,
        }


    except Exception as e:
        # 에러 발생 시 트랜잭션 롤백
        db.rollback()
        print(f"Exception occurred during address processing: {e}")
        raise HTTPException(status_code=500, detail=f"{e}, Failed to process address")
    
    
@app.post("/signup/address")
def signup(user: AddressCreate, db: Session = Depends(get_db)):

    try:
        # Address 처리
        existing_address = db.query(Address).filter_by(
            city=user.city, town=user.town, village=user.village
        ).first()

        if existing_address:
            # 이미 존재하는 경우, ID 반환
            return {
                "msg": "Address already exists",
                "address_id": existing_address.address_id,
            }

        # Address 생성
        new_address = Address(city=user.city, town=user.town, village=user.village)
        db.add(new_address)
        db.commit()
        db.refresh(new_address)

        return {
            "msg": "Address created successfully",
            "address_id": new_address.address_id,
        }


    except Exception as e:
        # 에러 발생 시 트랜잭션 롤백
        db.rollback()
        print(f"Exception occurred during address processing: {e}")
        raise HTTPException(status_code=500, detail="Failed to process address")