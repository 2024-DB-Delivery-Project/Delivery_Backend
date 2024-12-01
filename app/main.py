from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db
from app.models.models import User, Address
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt

# JWT 설정
SECRET_KEY = "q!w@e#r$"  # 강력한 키로 변경
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
    login_id: str
    password: str

class LoginRequest(BaseModel):
    login_id: str
    password: str


# 회원가입 API 
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    
    try:
        address = db.query(Address).filter(Address.address_id == user.address_id).first()
        if not address:
            raise HTTPException(status_code=400, detail="Invalid address_id")
        
        hased_password = get_password_hash(user.password)

        # 존재하지 않는 경우 새로 추가 
        new_user = User(
            name=user.name, 
            phone_number=user.phone_number, 
            role=user.role,
            address_id=user.address_id,
            login_id=user.login_id,
            password=hased_password
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

# 회원가입시, 주소 정보 추가 API
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



# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 비밀번호 해싱
def get_password_hash(password):
    return pwd_context.hash(password)

# 비밀번호 검증
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



# 사용자 조회
def get_user(db: Session, login_id: str):
    return db.query(User).filter(User.login_id == login_id).first()

# JWT 생성
def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": jwt.datetime.utcnow() + jwt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 사용자 인증
def authenticate_user(db: Session, login_id: str, password: str):
    user = get_user(db, login_id)
    if not user or not verify_password(password, user.password):
        return None
    return user


# 로그인 엔드포인트
@app.post("/login")
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    # 사용자 인증
    user = authenticate_user(db, user_data.login_id, user_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # JWT 생성
    access_token = create_access_token(data={"sub": user.name})
    return {"access_token": access_token, "token_type": "bearer", "user": user.name}
