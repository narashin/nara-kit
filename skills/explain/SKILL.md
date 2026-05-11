---
name: explain
description: "Generate shareable explanations of code, features, projects, or PRs tailored to a specific audience. Use when the user wants to explain something to another person — for example: '팀원한테 설명해줘', 'PM한테 어떻게 설명하지', '새 팀원 온보딩 문서 만들어줘', '이 PR 리뷰어한테 설명', '발표용 내용 정리해줘', '공유할 문서 만들어줘', '이 기능 walkthrough 써줘', '외부에 소개할 글'. Adapts format and depth based on audience (tech peer, new member, non-tech/PM, external) and scope (project, feature, method, PR)."
---

# Explain

기술 커뮤니케이터 역할로 작성한다 — 정확성과 독자 이해를 동시에 최적화.

코드/기능/프로젝트를 **타인에게 공유할 수 있는 설명**을 생성한다.
`explain-like-senior`(Claude가 나에게 학습 목적으로 설명)와 다르게, 이 스킬은 **내가 타인에게 전달할 콘텐츠**를 만든다.

## Step 1: 대상과 범위 파악

사용자 메시지에서 대상과 범위를 추론한다. 명시되지 않으면 묻는다.

**대상 (Audience)**

| 키워드 | 대상 | 깊이 |
|--------|------|------|
| 팀원, 동료, 리뷰어, peer | Tech peer | 구현 세부사항 + 설계 결정 근거 |
| 신규, 온보딩, 새 팀원 | New member | 프로젝트 전체 맥락 + 파일 지도 + 진입점 |
| PM, 기획자, 비개발자, non-tech | Non-tech | 기능 목적 + 사용자 영향 (코드 없음) |
| 발표, 컨퍼런스, 외부 | External | 문제 배경 + 접근 + 결과 |

**범위 (Scope)**

| 범위 | 탐색 전략 |
|------|----------|
| 프로젝트 전체 | CLAUDE.md/README → 디렉토리 구조 → 핵심 파일 3~5개 |
| 기능/피처 | 관련 컴포넌트/서비스/라우트 + 데이터 흐름 추적 |
| 메서드/함수 | 함수 본문 + 호출 컨텍스트 + 입출력 |
| PR/변경사항 | 변경 파일 목록 + 핵심 diff + 변경 이유 |

## Step 2: 코드 탐색

범위에 맞게 탐색한다. **코드를 읽어야 설명이 정확하다** — 추측 금지.

- 프로젝트: CLAUDE.md → 디렉토리 → 핵심 파일
- 기능: 관련 파일 → 데이터 흐름 (API → 상태 → 렌더링)
- 메서드: 함수 본문 → 참조 위치 (serena `find_referencing_symbols` 활용 가능)
- PR: `git diff` 또는 변경 파일 목록 → 핵심 변경사항

## Step 3: 설명 생성

대상에 맞는 형식을 사용한다. 각 형식의 템플릿은 `references/output-formats.md` 참조.

- Tech peer → Tech Peer 형식
- New member → New Member 형식
- Non-tech/PM → Non-tech 형식
- External/발표 → External 형식

### 예시

**입력**: "팀원한테 이 PR 어떻게 설명하지"
→ Tech peer 형식. `git diff` 확인 후 배경/구현 접근/변경 파일 섹션 생성.

**입력**: "PM한테 이 기능 설명해줘"
→ Non-tech 형식. 코드 없음. 사용자 시나리오 + 이전/이후 경험 중심.

**입력**: "새 팀원 온보딩 문서"
→ New member 형식. CLAUDE.md 읽어 스택 파악 → 핵심 폴더 지도 → 진입점 순서 작성.

## 출력 옵션

- **기본**: Markdown 문서. 길면 `docs/explain-{scope}.md`로 저장.
- **Brief**: 사용자가 "짧게", "슬랙에 올릴", "한 문단" 요청 시 핵심 불릿 5개 이내.

## 규칙

- 코드에서 확인된 사실만 작성. 추측 필요 시 `[UNVERIFIED]` 표기.
- Non-tech 대상이면 코드 스니펫 포함 금지.
- 사용자가 대상을 명시하지 않으면 Tech peer로 기본 가정하고 확인.
- 탐색해도 문서/코드가 없으면 작업 중단 후 "탐색 결과 없음" 보고.

## Additional Resources

- **`references/output-formats.md`** — 대상별 출력 형식 템플릿 (Tech Peer / New Member / Non-tech / External)
