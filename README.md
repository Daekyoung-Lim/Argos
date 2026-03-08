# Argos (아르고스) - KT 사내 자산 관리 시스템

**Argos(아르고스)**는 약 200명의 직원과 600개의 사내 자산을 효율적으로 관리하기 위해 구축된 스마트 자산 관리 시스템입니다. 직원이 스스로 자산을 점검할 수 있는 **자가 실사(Self-Survey)** 기능과 관리자가 자연어 질의(NL2SQL)를 통해 자산을 조회하고 엑셀로 내보낼 수 있는 지능형 챗봇 기능을 제공합니다.

---

## 🚀 주요 기능

### 1. 직원용: 스마트 자산 자가 실사 (Asset Self-Survey)
- **자산 목록 확인 및 실사 진행**: 할당된 자산 목록을 확인하고 직접 실사(Audit)를 진행할 수 있습니다.
- **AI 기반 사진 검증**: 스마트폰으로 자산 사진(스티커 및 자산 전체)을 촬영하여 업로드하면, AI(CrewAI - Asset Diligence Crew)가 사진 속 텍스트(OCR)와 메타데이터(GPS 및 시간)를 분석하여 해당 자산이 맞는지 자동으로 검증합니다 (3km/48h 오차 범위 내).

### 2. 관리자용: 지능형 자산 조회 챗봇 (Admin Analyst)
- **자연어 기반 DB 조회 (NL2SQL)**: "최근 1주일간 실사 완료된 노트북 목록 보여줘" 와 같이 자연어로 질문하면, AI(Admin Analyst Crew)가 SQL 쿼리로 변환하여 데이터베이스에서 결과를 조회합니다.
- **보고서 다운로드**: 조회된 결과를 마크다운 형식의 표로 확인하거나, 엑셀 파일(Excel)로 즉시 다운로드(수출)할 수 있습니다.

---

## 🛠 기술 스택 (Tech Stack)

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **AI Agent Framework**: **[CrewAI](https://crewai.com)** (멀티 에이전트 오케스트레이션)
  - `Asset Diligence Crew`: OCR, 메타데이터, DB 조회, 최종 검증 역할 분담
  - `Admin Analyst Crew`: 자연어→SQL 변환, 데이터 리포트 생성
- **Database ORM**: SQLAlchemy
- **Authentication**: JWT 인증

### Frontend
- **Framework**: React 18 (TypeScript 5.x) + Vite
- **Data Visualization**: Recharts

### Azure Services & AI Models
- **Database**: Azure SQL Database (위치 및 거리 계산 `STDistance()` 활용)
- **AI & LLM**: Azure OpenAI (GPT-4o)
- **Computer Vision (OCR)**: Azure AI Vision
- **Storage**: Azure Blob Storage (`argosstphotos/asset-photos` 컨테이너에 사진 및 Excel 파일 저장)

---

## 🏗 시스템 아키텍처

시스템은 보안 및 역할 분리를 위해 백엔드와 프론트엔드가 분리된 Web Application 구조(SPA)입니다. FastAPI 백엔드 내에서 CrewAI의 **2개의 독립된 Crew 시스템**을 운영합니다.

![아키텍처 스크린샷 (추가 예정)]() *(추후 추가)*

---

## ⚙️ 로컬 개발 환경 구성 가이드 (Quickstart)

시작하기 전에 각 환경에 맞는 의존성이 설치되어 있어야 합니다. (Python 3.11+, Node.js 18+, Docker Desktop)

### 1. 환경 변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래의 템플릿을 참고하여 Azure 리소스 키와 데이터베이스 정보를 입력합니다. (값은 보안을 위해 담당자에게 문의하세요.)

```env
```

### 2. 백엔드(Backend) 실행

```bash
# 1. backend 폴더로 이동
cd backend

# 2. 가상 환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. FastAPI 개발 서버 실행 (localhost:8000)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
👉 **API 문서(Swagger UI)**: http://localhost:8000/docs

### 3. 프론트엔드(Frontend) 실행

```bash
# 1. frontend 폴더로 이동
cd frontend

# 2. 패키지 설치
npm install

# 3. 개발 서버 실행 (localhost:5173)
npm run dev
```
👉 **웹 애플리케이션 접속**: http://localhost:5173

---

## 🐳 Docker를 이용한 백엔드 실행
Docker가 설치된 환경에서는 손쉽게 컨테이너 단위로 백엔드를 띄울 수 있습니다.

```bash
# 컨테이너 빌드
docker build -t argos-backend ./backend

# .env 환경 변수 파일을 마운트 하여 실행
docker run -p 8000:8000 --env-file .env argos-backend
```

---

## 📂 프로젝트 폴더 구조

```text
argos_draft_v01/
├── backend/                  # FastAPI 백엔드
│   ├── src/
│   │   ├── main.py           # 애플리케이션 진입점
│   │   ├── api/              # 라우터 엔드포인트 핸들러
│   │   ├── auth/             # JWT 기반 인증 로직
│   │   ├── models/           # SQLAlchemy DB 모델들
│   │   ├── services/         # 비즈니스 로직
│   │   ├── crews/            # CrewAI 에이전트 및 크루 구조 정의
│   │   └── tools/            # CrewAI 에이전트들이 사용할 외부 사용자 정의 도구 (OCR, SQL, Blob 등)
│   ├── tests/                # Pytest 단위 통합/테스트 코드
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # React 프론트엔드
│   ├── src/
│   │   ├── api/              # 백엔드 API 호출 클라이언트 설정
│   │   ├── auth/             # 프론트엔드 인증 컨텍스트
│   │   ├── components/       # 재사용 UI 컴포넌트
│   │   └── pages/            # View 단위 패이지 (직원용/관리자용 등)
│   ├── package.json
│   └── vite.config.ts
├── specs/                    # 시스템 개발 스펙 및 기획 문서
└── .env                      # 환경 변수 (포함되지 않음, 수동 생성 필요)
```

---

## 🚀 배포 (Deployment)
현재 배포 설정은 Azure 클라우드를 타겟으로 최적화되어 있습니다.
- **Backend**: **Azure Container Apps (ACA)** 상에 Docker 컨테이너 형태로 배포. 이미지 관리는 ACR(Azure Container Registry)을 이용합니다.
- **Frontend**: **Azure Static Web Apps** 로서 GitHub Actions를 통해 CI/CD 자동화 배포가 고려되어 있습니다.
