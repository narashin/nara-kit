# Sample spec

> 작성: 2026-07-08

## 1. 현황

- 활성 사용자 10명 <!-- src: users.csv | count rows where status=active -->
- 팀 수 3개 <!-- src: users.csv | distinct team -->
- 총 점수 780 <!-- src: users.csv | sum score -->
- 평균 응답 2.0초 <!-- src: latency.csv | avg response_ms / 1000 -->

## 2. 불일치가 있는 항목

- 코어 팀원 5명 <!-- src: users.csv | count rows where team=core -->

## 3. 매핑이 잘못된 항목

- 관리자 2명 <!-- src: users.csv | count rows where role=admin -->

## 4. 문법이 틀린 항목

- 대략 200명 <!-- src: users.csv (활성 사용자 수) -->

## 5. 마커 없는 수치

- 예상 트래픽 5000 rpm
- 목표 지연 300ms
