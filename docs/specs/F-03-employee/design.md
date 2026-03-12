# F-03 직원 관리 기술 설계

## 1. 개요
사장님이 직원 정보를 체계적으로 관리하여 근로계약서와 급여 계산에 활용하는 기능

## 2. API 설계

### 2.1 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | /api/v1/employees/ | 직원 등록 |
| GET | /api/v1/employees/ | 직원 목록 조회 |
| GET | /api/v1/employees/{id} | 직원 상세 조회 |
| PUT | /api/v1/employees/{id} | 직원 정보 수정 |
| PATCH | /api/v1/employees/{id}/resign | 직원 퇴직 처리 |

### 2.2 요청/응답 스키마

#### 직원 등록 요청
```json
{
  "name": "홍길동",
  "id_number": "900101-1234567",
  "nationality": "korean",
  "employment_type": "regular",
  "department": "영업팀",
  "position": "사원",
  "hire_date": "2024-01-15",
  "phone": "010-1234-5678",
  "email": "hong@company.com",
  "bank_name": "신한은행",
  "bank_account": "110-123-456789"
}
```

## 3. 에러 코드

| 코드 | HTTP | 설명 |
|------|------|------|
| E-5001 | 404 | 직원을 찾을 수 없음 |
| E-5002 | 409 | 이미 퇴직 처리된 직원 |
| E-5003 | 400 | 잘못된 퇴직일 |
| E-5004 | 422 | 주민등록번호 형식 오류 |
