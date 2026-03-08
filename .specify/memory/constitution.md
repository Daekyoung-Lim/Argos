<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- List of modified principles:
  - Added: I. 코드 품질 (Code Quality)
  - Added: II. 테스트 표준 (Testing Standards)
  - Added: III. 사용자 경험 일관성 (User Experience Consistency)
  - Added: IV. 성능 요구사항 (Performance Requirements)
- Added sections: 개발 워크플로우 (Development Workflow)
- Removed sections: 기존 예시 주석 및 불필요한 섹션 제거
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated)
  - .specify/templates/spec-template.md (✅ updated)
  - .specify/templates/tasks-template.md (✅ updated)
- Follow-up TODOs: 
  - RATIFICATION_DATE 확인 필요
-->
# Argos Constitution

## 핵심 원칙 (Core Principles)

### I. 코드 품질 (Code Quality)
모든 코드는 유지보수성, 가독성, 재사용성을 최우선으로 작성되어야 합니다.
- 정적 분석 및 린트(Lint) 도구 사용을 의무화합니다.
- 복잡한 로직 지양: 모듈은 단일 책임 원칙(SRP)을 준수해야 합니다.
- 모든 주요 함수와 클래스에는 명확한 문서화(Docstring 등)를 포함해야 합니다.

### II. 테스트 표준 (Testing Standards)
안정적인 서비스 제공을 위해 철저한 테스트를 거쳐야 합니다. (NON-NEGOTIABLE)
- TDD(Test-Driven Development) 지향: 새로운 기능 개발 시 반드시 단위 테스트(Unit Test)를 작성해야 합니다.
- 핵심 비즈니스 로직에 대해 높은 테스트 커버리지(예: 80% 이상)를 유지해야 합니다.
- API 및 모듈 간 상호작용은 통합 테스트(Integration Test)를 통해 검증해야 합니다.

### III. 사용자 경험 일관성 (User Experience Consistency)
사용자에게 직관적이고 일관된 디자인 및 상호작용을 제공해야 합니다.
- 프로젝트 전체에서 통일된 디자인 시스템(색상, 타이포그래피, 컴포넌트 등)을 사용합니다.
- 상태 변화(로딩, 에러, 성공 등)에 대해 사용자에게 명확한 피드백을 제공해야 합니다.
- 웹/앱 접근성(Accessibility) 가이드라인을 고려하여 개발합니다.

### IV. 성능 요구사항 (Performance Requirements)
효율적인 리소스 사용과 빠른 응답 속도를 보장해야 합니다.
- 성능 예산(Performance Budget) 준수: 응답 시간 목표치(예: <200ms) 및 최대 메모리 사용량을 초과하지 않도록 최적화합니다.
- 프론트엔드의 경우 초기 로딩 속도 및 렌더링을 지속적으로 모니터링하고 개선합니다.
- 불필요한 자원 낭비를 막기 위한 주기적인 성능 프로파일링을 수행합니다.

## 개발 워크플로우 (Development Workflow)

- **코드 리뷰 필수**: 모든 변경 사항은 병합(Merge) 전 동료의 리뷰 및 승인을 받아야 합니다.
- **오류 방지 프로세스**: CI/CD 파이프라인에서 정적 분석 및 테스트가 성공적으로 통과해야만 배포될 수 있습니다.

## 거버넌스 (Governance)

- 본 헌장(Constitution)의 원칙들은 다른 린트 규칙이나 기존 관행보다 우선합니다.
- 헌장에 명시된 프로세스를 우회해야 할 경우, 합당한 이유를 문서로 남기고 승인을 받아야 합니다.
- 헌장 수정 시에는 버전(MAJOR/MINOR/PATCH)을 갱신하고 수정 내역을 명시해야 합니다.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2026-03-03
