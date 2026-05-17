# Component Pick Procedure — Frontend Catalog-First Gate

Frontend 작업(UI 컴포넌트 신규 작성 또는 수정)에서 **카탈로그 우회 직접 작성을 차단**하는 5단계 절차.

## 적용 조건

다음 중 하나 이상이면 본 절차 적용 필수:

- 작업이 React/Vue/Svelte/Solid 등 컴포넌트 라이브러리 코드 신규 추가/수정
- `*.tsx`, `*.jsx`, `*.vue`, `*.svelte` 파일 신규 작성
- 디자인 시스템/UI 키트가 프로젝트에 존재 (package.json에 `iris-ui`, `@chakra-ui`, `mui`, `radix`, 자체 `ui-kit` 등)
- 프로젝트에 `DESIGN.md` 또는 `component-catalog.md` 존재

조건 미해당 시(예: utility/hook/state 코드만 변경) 본 절차 skip 가능.

## 5단계 절차

### Step 1 — 카탈로그 직접 매칭

`DESIGN.md` / `component-catalog.md` / 디자인 시스템 패키지 docs를 **우선** 조회.

- 요구된 기능을 표현 가능한 컴포넌트가 카탈로그에 **있는 그대로** 존재하는가?
- 있으면 → 즉시 사용. 종료.

### Step 2 — Optional props로 해결 가능?

Step 1에서 정확 매칭 없으면, 유사 컴포넌트 + optional props로 커버 가능 여부 확인.

- 예: `Button`은 있는데 `loading` prop 없음 → `Button` + 외부 spinner 합성으로 해결
- 가능하면 → 합성 사용. 종료.

### Step 3 — 코드베이스 grep (카탈로그 누락 가능성)

카탈로그가 stale일 수 있음. 실제 코드베이스에서 grep:

```
grep -r "export.*Component" src/components/
grep -r "<TargetName" src/
```

- 발견되면 → Step 4로
- 발견 안 되면 → Step 5로

### Step 4 — 카탈로그 업데이트 + 사용

Step 3에서 발견했으나 카탈로그에 누락된 경우:

1. `DESIGN.md` 또는 `component-catalog.md`에 항목 추가 (`/design-md update` 활용 가능)
2. 해당 컴포넌트 사용
3. trailing 출력에 카탈로그 업데이트 사실 명시

### Step 5 — STOP & 승인 요청 (gate)

Step 1-4 모두 실패 시 **신규 컴포넌트 직접 작성 금지**. 사용자에게 승인 요청 필수:

```
[COMPONENT-PICK] catalog miss

요구: <기능 한 줄 요약>
시도: catalog(X) / optional-props(X) / codebase-grep(X)

제안 신규 컴포넌트:
- 이름: <Component>
- 위치: <path>
- props: <interface 요약>
- 카탈로그 등록 여부: yes/no
- 재사용 예상 위치: <N곳>

진행할까요? (확인 받기 전 코드 작성 금지)
```

`AskUserQuestion` 호출 후 명시 승인 받아야 코드 작성 진입.

**Skip 불가**: 이 단계는 `--auto`로도 우회 금지. 신규 컴포넌트는 코드베이스에 영구 영향 — 사용자 결정 사항.

## Trailing 출력 의무

frontend 작업 완료 후 응답에 한 줄 추가:

```
[COMPONENT-PICK] catalog_hits=N | optional_props=N | new_components=N | catalog_updates=N
```

- `new_components` > 0 이면 Step 5 승인 받았음을 의미

## 예시

### 예시 1 — 카탈로그 hit

```
요구: 모달로 사용자 정보 표시
Step 1: iris-ui `<Modal>` 존재 → 사용
[COMPONENT-PICK] catalog_hits=1 | optional_props=0 | new_components=0 | catalog_updates=0
```

### 예시 2 — Step 4 (카탈로그 stale)

```
요구: 별점 표시 UI
Step 1: catalog miss
Step 2: optional props 미적용
Step 3: grep → `src/components/RatingStars.tsx` 발견
Step 4: DESIGN.md에 RatingStars 추가 + 사용
[COMPONENT-PICK] catalog_hits=0 | optional_props=0 | new_components=0 | catalog_updates=1
```

### 예시 3 — Step 5 (신규 필요)

```
요구: 드래그 가능한 칸반 카드
Step 1-3: 모두 miss
Step 5: 사용자에게 KanbanCard 신규 생성 승인 요청
[승인 후]
[COMPONENT-PICK] catalog_hits=0 | optional_props=0 | new_components=1 | catalog_updates=1
```
