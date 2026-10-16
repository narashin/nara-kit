# Handoff — CSV 내보내기 1차 구현

## 1. 현재 목표
주문 리포트 CSV 내보내기를 완성한다.

## 2. 작성 시점 context
- branch: `feature/PROJ-123-csv-export`
- HEAD: `a4dd02c`
- working tree: clean
- timestamp: 2026-10-14T18:00:00+09:00

## 4. 진행 중 작업 (In Progress)
- 헤더 행 로캘: 한국어/영어 중 무엇으로 낼지 결정 대기, 영어로 가다가 기획 확인 필요해서 멈춤
- 대용량 스트리밍: 10만 행 이상에서 메모리 급증, 스트림 API로 바꾸던 중

## 5. 열린 질문 (Open Questions)
- Q1: 금액 열에 통화 기호를 붙이나?

## 9. 먼저 읽을 핵심 파일
- `src/report/export.ts` — 내보내기 진입점
