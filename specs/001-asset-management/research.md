# Research: Company Asset Management (001-asset-management)

**Date**: 2026-03-04  
**Branch**: `001-asset-management`  
**Spec**: [spec.md](./spec.md)

## 1. CrewAI as AI Agent Framework

### Decision
CrewAI를 AI Agent 오케스트레이션 프레임워크로 사용한다. 두 개의 독립 Crew로 구성한다.

### Rationale
- 역할(Role) 기반의 멀티 에이전트 시스템을 선언적으로 구성 가능
- Agent → Task → Crew 계층 구조가 자산 실사 파이프라인(순차 실행)과 NL2SQL 파이프라인(순차 실행)에 자연스럽게 매핑됨
- 보안 분리: Employee 기능(Asset Diligence Crew)과 Admin 기능(Admin Analyst Crew)을 별도 Crew로 격리

### Alternatives Considered
- **LangGraph**: 그래프 기반 워크플로우에 강하지만 사용자 요구사항이 CrewAI를 명시
- **AutoGen**: 대화형 에이전트에 적합하나 역할 기반 파이프라인에는 CrewAI가 더 간결

---

## 2. Azure AI Vision (OCR)

### Decision
Azure AI Vision (Computer Vision v4.0 Read API)을 사용하여 자산 스티커 사진에서 10자리 자산 코드를 추출한다.

### Rationale
- Azure 생태계 내에서 완전 관리형(managed) OCR 서비스
- 한국어 및 숫자 인식에 우수한 성능
- QR 코드 인식도 지원하여 자산 코드를 이중 검증 가능

### Alternatives Considered
- **Tesseract (on-premises)**: 무료이나 정확도 및 관리 비용 문제
- **Google Vision API**: 우수하나 Azure 전용 인프라 정책에 위배

---

## 3. EXIF 메타데이터 추출

### Decision
Python `Pillow` 라이브러리의 EXIF 파싱 기능을 사용하여 GPS 좌표 및 촬영 시각을 추출한다.

### Rationale
- 외부 API 호출 불필요, 서버 내에서 즉시 처리 가능
- GPS 좌표(위도/경도)와 DateTimeOriginal 태그를 표준적으로 지원
- 의존성이 가벼움 (Pillow는 이미 이미지 처리용으로 사용)

### Alternatives Considered
- **exiftool (subprocess)**: 강력하나 별도 바이너리 설치 필요
- **piexif**: 가볍지만 Pillow보다 커뮤니티 지원이 적음

---

## 4. 거리 계산 (SQL Server STDistance)

### Decision
실제 DB가 `geography` 공간 타입을 사용하므로, SQL Server의 `STDistance()` 함수로 거리를 계산한다. Python 측 Haversine 계산은 불필요.

### Rationale
- 실제 DB의 `Assets.registered_location`과 `AuditLogs.detected_location`이 이미 `geography` 타입으로 정의됨
- `registered_location.STDistance(detected_location)` → 미터 단위 거리 반환, 3000m 이하 비교에 최적
- `AuditLogs.distance_meters` 컬럼에 계산된 거리를 사전 저장하는 구조가 이미 마련됨
- DB 레벨에서 처리하므로 애플리케이션 코드 단순화

### Alternatives Considered
- **Python Haversine (geopy)**: 가능하나 DB가 이미 geography 타입을 지원하므로 불필요한 중복
- **Azure Maps**: 과도한 비용

---

## 5. NL2SQL (자연어 → SQL 변환)

### Decision
Azure OpenAI GPT-4.1 (gpt-4.1 deployment)을 사용하여 자연어 질의를 SQL로 변환한다. 데이터베이스 스키마를 System Prompt에 포함하고 Read-only 쿼리만 실행한다.

### Rationale
- 사용자가 명시한 Azure OpenAI 리소스를 활용
- GPT-4.1의 우수한 SQL 생성 능력
- Read-only 권한으로 안전성 확보

### Alternatives Considered
- **LangChain SQL Agent**: 유연하지만 CrewAI Agent 내부 Tool로 직접 구현하는 것이 더 통합적

---

## 6. Excel 내보내기

### Decision
`openpyxl` 라이브러리를 사용하여 서버 측에서 .xlsx 파일을 생성하고, Azure Blob Storage에 업로드한 후 SAS URL을 반환한다.

### Rationale
- Python에서 가장 널리 사용되는 .xlsx 생성 라이브러리
- 메모리 효율적이며 10,000행 이상도 빠르게 처리
- Blob Storage에 저장하여 서버 로컬 파일시스템 의존 제거

### Alternatives Considered
- **pandas to_excel**: 편리하지만 pandas 전체 의존성이 무거움

---

## 7. 인증 방식

### Decision
JWT(JSON Web Token) 기반 인증을 사용한다. FastAPI의 `python-jose` + `passlib` 조합으로 구현한다.

### Rationale
- 상태비저장(stateless) 인증으로 AKS 환경에서 수평 확장에 유리
- Role claim에 'employee' / 'admin' 값을 포함하여 역할 기반 접근 제어
- Azure AD/Entra ID 통합은 PoC 후 고려 가능

### Alternatives Considered
- **Azure AD/Entra ID**: 엔터프라이즈급이나 PoC 단계에서는 과도한 설정
- **Session-based**: 상태 관리와 AKS 스케일링 시 복잡성 증가

---

## 8. Frontend 기술 스택

### Decision
React + TypeScript를 사용하며, Azure Static Web Apps에 배포한다. 차트 라이브러리로 Recharts를 사용한다.

### Rationale
- 풍부한 인터랙티브 UI 생성이 용이 (Admin 채팅 + Dashboard 동시 표시)
- TypeScript로 프론트엔드 타입 안정성 확보
- Azure Static Web Apps는 React SPA와 자연스럽게 통합
- Recharts: React 기반 선언적 차트 라이브러리로 대시보드 구현에 적합

### Alternatives Considered
- **Vue.js**: 충분하지만 React 생태계가 더 풍부
- **Chart.js**: 좋지만 React 통합은 Recharts가 더 자연스러움

---

## 9. Backend 컨테이너화 및 배포

### Decision
FastAPI 백엔드를 Docker 이미지로 빌드하여 ACR(Azure Container Registry)에 Push하고, **ACA(Azure Container Apps)**에 배포한다.

### Rationale
- PoC 프로젝트에 최적: Kubernetes 클러스터 관리 없이 컨테이너 배포 가능
- 내장 HTTPS Ingress, 환경변수/시크릿 관리 제공
- Serverless 모드로 0으로 스케일 가능 → 유휴 비용 최소화
- 프로덕션 전환 시 AKS로 마이그레이션 용이 (동일 Docker 이미지 사용)

### Alternatives Considered
- **AKS**: 전체 Kubernetes 기능이지만 PoC에는 컨트롤 플레인/노드 비용이 과도
- **ACI**: 가장 단순하지만 Ingress/스케일링/리비전 관리 가 없음
- **Azure App Service (Container)**: 가능하지만 ACA 대비 유연성 부족

---

## 10. Azure SQL Database 스키마 전략

### Decision
기존 스키마(Users, Assets, AuditLogs, Departments, AssetCategories)를 그대로 활용한다. NL2SQL 대화 기록을 위한 `ChatLogs` 테이블 1개만 신규 생성하였다. (✅ 생성 완료)

### Rationale
- 기존 데이터(200명 직원, 600개 자산) 및 5개 테이블, FK 관계 모두 보존
- 위치 데이터는 SQL Server `geography` 공간 타입을 활용 (lat/lng 분리 불필요)
- `AuditLogs` 테이블이 이미 실사 기록용으로 충분한 컬럼 보유 (is_verified, verification_msg, distance_meters 등)

### Alternatives Considered
- **전면 재설계**: 기존 데이터 마이그레이션 비용 과다

---

## 11. Azure Blob Storage (파일 저장)

### Decision
Azure Blob Storage (`argosstphotos` 계정, `asset-photos` 컨테이너)를 사용하여 실사 사진 및 Excel 내보내기 파일을 저장한다.

### Rationale
- 이미지와 파일을 서버 로컬이 아닌 Azure 관리형 오브젝트 스토리지에 저장하여 AKS Pod 재시작/스케일링에 무관하게 영속성 보장
- SAS(Shared Access Signature) URL을 생성하여 클라이언트가 직접 다운로드 가능
- 실사 사진 업로드 시 `audit-photos/{user_id}/{audit_id}.jpg` 경로로 정리하여 추적 용이
- Excel 파일은 `exports/{admin_user_id}/{timestamp}.xlsx` 경로로 저장
- DB에는 Blob URL만 저장하여 DB 부하 감소

### 용도별 Blob 구조
```
asset-photos/
├── audit-photos/          # 실사 촬영 사진
│   ├── {user_id}/
│   │   └── {audit_id}.jpg
├── exports/               # NL2SQL 결과 Excel 파일
│   ├── {admin_user_id}/
│   │   └── {timestamp}.xlsx
```

### Alternatives Considered
- **서버 로컬 파일시스템**: AKS Pod 재시작 시 파일 소실
- **Azure Files (SMB)**: 파일 공유에 적합하나, 오브젝트 스토리지가 이미지/파일 저장에 더 적합
