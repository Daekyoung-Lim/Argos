# API Contracts: Company Asset Management (001-asset-management)

**Date**: 2026-03-04 (Updated)  
**Branch**: `001-asset-management`  
**Base URL**: `https://<aks-domain>/api/v1`

---

## Authentication

### POST /auth/login

사용자 인증 및 JWT 토큰 발급

**Request Body**:
```json
{
  "employee_no": "string",
  "password": "string"
}
```

**Response 200**:
```json
{
  "access_token": "string (JWT)",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "employee_no": "EMP001",
    "name": "홍길동",
    "email": "hong@kt.com",
    "role": "Employee",
    "department": {
      "dept_id": 3,
      "dept_name": "네트워크본부"
    }
  }
}
```

**Response 401**: `{ "detail": "Invalid credentials" }`

---

## Employee Endpoints

### GET /assets/my

로그인 된 직원에게 할당된 자산 목록 조회 (JWT 필수)

**Headers**: `Authorization: Bearer <token>`

**Response 200**:
```json
{
  "assets": [
    {
      "asset_id": 1,
      "asset_code": "1234567890",
      "asset_name": "노트북 Dell XPS 15",
      "category": {
        "category_id": 1,
        "category_name": "IT장비"
      },
      "registered_address": "서울시 종로구 세종대로 178",
      "status": "Active",
      "last_audit_date": "2025-12-01T10:30:00Z",
      "last_condition": "양호"
    }
  ],
  "total": 3
}
```

---

### POST /audit/submit

자산 실사 사진 제출 (JWT 필수, Employee only)

**Headers**: `Authorization: Bearer <token>`

**Request** (multipart/form-data):
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| image | file | Yes | 자산 스티커 사진 (JPEG/PNG) |
| asset_code | string | Yes | 대상 자산의 10자리 코드 |
| asset_condition | string | Yes | 자산 상태 (양호/불량/수리필요) |

**Response 200** (성공):
```json
{
  "is_verified": true,
  "audit_id": 42,
  "asset_code": "1234567890",
  "photo_url": "https://argosstphotos.blob.core.windows.net/asset-photos/audit-photos/1/42.jpg",
  "details": {
    "ocr_asset_code": "1234567890",
    "code_match": true,
    "detected_address": "서울시 종로구 세종대로 근처",
    "distance_meters": 380.5,
    "location_match": true,
    "photo_taken_at": "2026-03-03T14:30:00Z",
    "time_match": true
  },
  "verification_msg": "자산 실사가 성공적으로 완료되었습니다."
}
```

**Response 200** (실패):
```json
{
  "is_verified": false,
  "audit_id": 43,
  "asset_code": "1234567890",
  "details": {
    "ocr_asset_code": "1234567891",
    "code_match": false,
    "distance_meters": 150.2,
    "location_match": true,
    "time_match": true
  },
  "verification_msg": "자산 코드가 일치하지 않습니다. 추출된 코드: 1234567891"
}
```

**Response 400**: `{ "detail": "Image metadata missing GPS information" }`

---

## Admin Endpoints

### POST /admin/chat

NL2SQL 자연어 질의 (JWT 필수, Admin only)

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "query": "실사를 완료하지 않은 직원 목록을 보여줘"
}
```

**Response 200**:
```json
{
  "query": "실사를 완료하지 않은 직원 목록을 보여줘",
  "generated_sql": "SELECT u.name, u.email, d.dept_name FROM Users u LEFT JOIN Departments d ON u.dept_id = d.dept_id LEFT JOIN Assets a ON u.user_id = a.current_holder_id WHERE a.last_audit_date IS NULL OR a.last_audit_date < '2026-01-01'",
  "columns": ["name", "email", "dept_name"],
  "rows": [
    ["김철수", "kim@kt.com", "경영기획본부"],
    ["이영희", "lee@kt.com", "네트워크본부"]
  ],
  "total_rows": 2,
  "log_id": 15
}
```

**Response 400**: `{ "detail": "Unable to understand the query. Please rephrase." }`

---

### GET /admin/chat/export/{log_id}

채팅 결과를 Excel 파일로 다운로드 (JWT 필수, Admin only)

**Headers**: `Authorization: Bearer <token>`

**Response 200**:
```json
{
  "download_url": "https://argosstphotos.blob.core.windows.net/asset-photos/exports/1/20260304_153000.xlsx?sv=...&sig=...",
  "file_name": "asset_query_2026-03-04.xlsx",
  "expires_in_minutes": 60
}
```

**Response 404**: `{ "detail": "Chat log not found" }`

---

## Common Error Responses

| Status | Description |
|--------|-------------|
| 401 | Unauthorized - Invalid or missing JWT token |
| 403 | Forbidden - Insufficient role permissions |
| 422 | Validation Error - Invalid request format |
| 500 | Internal Server Error |
