---
name: reflect
description: >-
  Capture session learnings — technical decisions, conventions, and warnings — and save to memory.
  USE FOR: "reflect", "세션 마무리", "오늘 배운 것", "결정 기록", "session end learnings".
  DO NOT USE FOR: code review, gap analysis, commit message generation.
---

# reflect — 세션 학습 캡처

세션에서 내린 결정, 발견한 컨벤션, 주의사항을 구조화하여 프로젝트 지식으로 저장한다.

## 수집 (병렬 실행)

1. **세션 히스토리**: 이번 대화에서 내린 기술 결정 회고
2. **Git diff**: `git diff main...HEAD --stat` 또는 최근 커밋 목록
3. **gap.md 변화**: gap.md 있으면 점수 변화 확인
4. **발견된 패턴**: 세션 중 발견한 코드 컨벤션이나 프로젝트 특이사항

## 분류

- **Decisions**: 기술적/설계적 결정 + 이유
- **Conventions**: 발견하거나 확립한 코드 컨벤션
- **Warnings**: 다음 세션 주의사항 (코드만 봐서 알 수 없는 것)

## 저장

1. **Auto-memory**: 다음 세션에도 유효한 Decisions/Warnings → memory 저장
2. **docs/learnings.md**: 팀 공유 필요 시, 파일 존재 시만 append
3. **gap.md**: Agreed Exceptions 변경 시 반영

## 출력

`## Session Reflect — {날짜}` 헤더 아래 Decisions, Conventions, Warnings, Gap Status (이전→현재), Next Session 각 섹션 출력.

## 규칙

- `git log`로 볼 수 있는 코드 변경 내역 나열 금지
- 결정의 **이유** 필수
- Conventions는 프로젝트 전반 적용 가능한 것만
- Warnings는 코드만 봐서 알 수 없는 것만
- 저장할 내용 없으면 "특이사항 없음" 출력 후 종료
