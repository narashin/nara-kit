# 실행 세부 — 전략 · 위임 · TDD · 리뷰 경계

## 전략 제안 형식

조사 후 실행 모드와 TDD 여부를 이유와 함께 한 번에 제안한다. 사용자가 일부만 정했다면 나머지만 묻는다.

```text
구현 전략을 제안합니다.
- 실행: direct|delegated — 이유: ...
- TDD: 사용|미사용 — 이유: ...
- 완료: 관련 검증 후 staged 상태로 정지 (커밋은 /nara-commit)
이 전략으로 진행할까요?
```

- `direct` 우선: 작은 변경, 공유·강결합 파일, 긴밀한 구현-검증 반복.
- `delegated` 고려: 독립 범위·완료 조건이 명확하고 격리 가치가 클 때만.
- TDD 권장: 공개 동작 경계·회귀 위험이 명확할 때. non-TDD 권장: 문구·설정·기계적 변경, 유용한 seam 없음.

## TDD 루프 (승인 시)

의미 있는 공개 동작 경계를 골라 수직 slice 하나의 focused test를 쓰고, **실제 실행해 red를 관찰**한 뒤 최소 구현으로 green을 만들고 재실행한다. 핵심 loop는 `red → green`이며 refactor를 매 cycle 강제하지 않는다. 이미 통과하는 테스트를 red로 표현하거나, 내부 구현을 테스트하거나, 테스트를 위해 production API를 왜곡하지 않는다. 유용한 seam이 없으면 TDD를 강제하지 않는다.

## 위임 정의

`direct`는 현재 에이전트가 구현 책임을 직접 소유한다. context-mode·MCP·검색·정적 분석·브라우저·샌드박스·subprocess·테스트 러너·formatter·linter·typechecker 사용은 direct와 양립하며 delegation이 **아니다**.

`delegated`는 독립 자율 implementor 에이전트 **한 명**에게 구현 책임을 넘긴다. 단순 도구 사용이나 subprocess 실행을 delegated로 분류하지 않는다.

## 위임 판단

Direct를 우선한다:

- 변경이 작거나 기계적이다.
- 하나 또는 소수 파일에 집중된다.
- 공유·강결합 코드를 수정한다.
- 현재 컨텍스트가 충분하다.
- 구현과 검증을 긴밀히 반복해야 한다.
- 분리 비용이 구현 비용보다 크다.

Delegated 고려:

- 범위·완료 조건을 독립적으로 전달할 수 있다.
- 관련 파일·결정이 충분히 명확하다.
- 공유 파일 충돌 가능성이 낮다.
- 메인 컨텍스트 보존 또는 작업 격리 가치가 크다.
- 설계보다 독립 구현 수행이 주 작업이다.

**작업이 크다는 이유만으로 delegated를 선택하지 않는다.**

## Implementor 계약

Implementor 한 명에게 전달한다: 목표·포함/제외 범위 · 관련 파일·진입점 · 확정된 결정과 승인된 TDD 여부 · 검증 명령·기대치 · 금지 행동 · 반환할 diff·검증 결과·남은 위험.

Implementor는 다른 에이전트를 만들거나 재위임하지 않고, 사용자 호출형 nara-kit 스킬을 실행하지 않으며, 범위를 확대하거나 무관한 리팩터링을 섞지 않는다. commit·push·PR·merge·tag·release·publish도 하지 않는다.

현재 에이전트가 실제 diff·요청 준수·검증 증거를 확인한다. 필요하면 명확한 수정 지시를 한 번 내리고 회귀 검증한다. 검토 없이 결과를 수용하지 않는다. 최종 검증과 정지 책임은 현재 에이전트에 있다.

## 리뷰 경계

리뷰는 direct/delegated 선택과 별개인 선택적 품질 단계다. implementor와 reviewer는 다른 역할이며 implementor를 독립 reviewer로 계산하지 않는다.

인증·결제·개인정보·권한·마이그레이션·데이터 손실 가능성·동시성·공개 API·대규모 구조 변경 또는 테스트하지 않은 고위험 코드에만 reviewer 한 명을 고려한다.

최대 흐름:

```text
implementation → review once → fix once → regression verification → stop
```

reviewer fan-out, reviewer의 재위임, 자동 재리뷰, 발견 사항이 없을 때 추가 reviewer 실행, 리뷰 결과를 이유로 한 전체 구현 재위임을 금지한다. 수정이 필요하면 한 번 반영하고 기존 발견 사항·관련 회귀를 검증한 뒤 종료한다.

독립적·전면적 리뷰가 필요하면 이 경량 리뷰 대신 `/nara-code-review`(multi-agent)를 별도 단계로 호출한다.
