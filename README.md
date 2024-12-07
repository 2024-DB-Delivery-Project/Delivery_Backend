# 배송 관리 시스템 (Backend)

## 프로젝트 설명
이 프로젝트는 고객, 판매자, 배송 회사, 그리고 배송 기사를 위한 통합 배송 관리 시스템의 백엔드입니다.  
사용자는 각자의 역할에 따라 주문, 배송 상태 관리, 물품 확인 등을 수행할 수 있습니다.  
FastAPI를 기반으로 구현되었으며, SQLAlchemy를 사용하여 데이터베이스와 상호작용합니다.

---

## 주요 기능

### 공통
- **JWT 기반 인증 및 권한 관리**
  - 모든 사용자 요청은 JWT 토큰을 통해 인증됩니다.

---

### 고객 (Customer)
- **구매 제품 리스트 확인**
  - **API**: `GET /customers/bought_list`
  - 고객이 구매한 제품 목록을 조회합니다.
  - **SQL Feature**: `JOIN`, `SELECT`

- **배송 상태 확인**
  - **API**: `POST /customers/delivery_status`
  - 고객의 주문에 대한 현재 배송 상태를 확인합니다.
  - **SQL Feature**: `JOIN`, `WHERE`

---

### 판매자 (Seller)
- **판매 제품 및 주문 목록 확인**
  - **API**: `GET /seller/products`
  - 판매자가 등록한 제품과 관련된 주문 정보를 조회합니다.
  - **SQL Feature**: `JOIN`, `GROUP BY`

- **물류 담당자 지정**
  - **API**: `POST /seller/select_logistic`
  - 특정 주문에 대해 물류 담당자를 지정하고 상태를 갱신합니다.
  - **SQL Feature**: `UPDATE`, `INSERT`

---

### 배송 회사 (Logistic)
- **배송할 제품 확인**
  - **API**: `GET /logistic/deliveries`
  - 물류 담당자가 담당하는 배송 목록을 조회합니다.
  - **SQL Feature**: `JOIN`, `GROUP BY`

- **운전기사 배정**
  - **API**: `POST /logistic/assign_driver`
  - 특정 배송 건에 운전기사를 배정하고 상태를 갱신합니다.
  - **SQL Feature**: `UPDATE`, `INSERT`

---

### 운전자 (Driver)
- **배송 목록 조회**
  - **API**: `GET /driver/deliveries`
  - 운전자가 담당하는 배송 목록을 확인합니다.
  - **SQL Feature**: `SELECT`, `WHERE`

- **배송 완료 처리**
  - **API**: `POST /driver/complete_delivery`
  - 배송 완료 후 상태를 갱신하고 기록을 삭제합니다.
  - **SQL Feature**: `UPDATE`, `DELETE`

---

## 기술 스택
- **프로그래밍 언어**: Python 3.9
- **프레임워크**: FastAPI
- **데이터베이스**: PostgreSQL
- **ORM**: SQLAlchemy
- **인증**: JWT
- **배포**: Uvicorn

---

## 데이터베이스 구조

### 주요 테이블
- `users`: 사용자 정보 (고객, 판매자, 물류 담당자, 운전자)
- `products`: 제품 정보
- `orders`: 주문 정보
- `deliveryinfo`: 배송 정보
- `driverdeliveryinfo`: 운전자별 배송 정보