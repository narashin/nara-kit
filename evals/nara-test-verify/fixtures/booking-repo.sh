#!/usr/bin/env bash
# Build a throwaway repo for the nara-test-verify critic tasks.
# Usage: booking-repo.sh <empty-dir> [recheck]
# A meeting-room booking module with requirements, a plan and a discover-schema
# scenarios file. Planted gaps: AC-3 (cancel frees the slot) has no scenario,
# S3-04 asserts an internal list, S3-05 asserts a field no document defines, and
# the overlap check misses a booking that fully contains an existing one.
# `recheck` adds a prior review and a second commit that rewrites S3-04 and adds
# S3-06 for AC-3, so a correct re-run re-checks only those two IDs.
set -euo pipefail
dir="${1:?usage: booking-repo.sh <empty-dir> [recheck]}"
mode="${2:-}"
mkdir -p "$dir"
if [ -n "$(ls -A "$dir")" ]; then
  echo "refusing: $dir is not empty (pass a fresh dir, e.g. \"\$(mktemp -d)\")" >&2
  exit 2
fi
cd "$dir"
git init -q -b main
git config user.name "dev" && git config user.email "dev@example.com"

mkdir -p src docs/test-scenarios
cat > src/booking.py <<'PY'
from datetime import datetime


class Conflict(Exception):
    pass


class PastTime(Exception):
    pass


class Rooms:
    def __init__(self, now=datetime.now):
        self._bookings = []
        self._now = now

    def book(self, room, start, end, user):
        if start < self._now():
            raise PastTime()
        for b in self._bookings:
            if b["room"] != room:
                continue
            starts_inside = b["start"] <= start < b["end"]
            ends_inside = b["start"] < end <= b["end"]
            if starts_inside or ends_inside:
                raise Conflict()
        booking = {"id": len(self._bookings) + 1, "room": room,
                   "start": start, "end": end, "user": user}
        self._bookings.append(booking)
        return booking

    def cancel(self, booking_id):
        self._bookings = [b for b in self._bookings if b["id"] != booking_id]
PY

cat > docs/requirements.md <<'MD'
# 회의실 예약 요구사항

## Acceptance Criteria
- AC-1: 비어 있는 시간에 예약하면 예약 id를 돌려준다.
- AC-2: 같은 회의실에서 시간이 조금이라도 겹치면 예약을 거부한다(Conflict).
- AC-3: 예약을 취소하면 그 시간을 다시 예약할 수 있다.
- AC-4: 현재 시각보다 이른 시작 시각은 거부한다(PastTime).

## Edge Cases
- 앞 예약의 끝 시각과 새 예약의 시작 시각이 같으면 겹침이 아니다.
MD

cat > docs/plan.md <<'MD'
# Booking Plan

## Technical Context
- 구현: `src/booking.py`의 `Rooms.book`, `Rooms.cancel`
- 테스트: pytest, 시각은 `now` 주입으로 고정한다

## T-1 예약 생성과 겹침 거부
AC-1, AC-2, AC-4. 대상 `src/booking.py`.
MD

cat > docs/test-scenarios/scenarios-detailed.md <<'MD'
# Booking Test Scenarios (S3 selected 5 / S2 candidates 9)

### S3-01 빈 시간 예약 성공
- **AC-ID**: AC-1
- **진입경로**: `Rooms.book("A", 10:00, 11:00, "kim")`
- **실행역할**: 일반 사용자
- **독립 실행**: 가능
- **기대**: 예약 id 1을 돌려준다

### S3-02 시작이 겹치면 거부
- **AC-ID**: AC-2
- **진입경로**: 10:00-11:00 예약 뒤 10:30-11:30 예약
- **실행역할**: 일반 사용자
- **독립 실행**: 가능
- **기대**: Conflict

### S3-03 과거 시각 거부
- **AC-ID**: AC-4
- **진입경로**: now=12:00에서 09:00-10:00 예약
- **실행역할**: 일반 사용자
- **독립 실행**: 가능
- **기대**: PastTime

### S3-04 예약이 저장된다
- **AC-ID**: AC-1
- **진입경로**: 10:00-11:00 예약
- **실행역할**: 일반 사용자
- **독립 실행**: 가능
- **기대**: `rooms._bookings` 길이가 1이다

### S3-05 끝-시작이 맞닿으면 허용
- **AC-ID**: AC-2
- **진입경로**: S3-01 다음에 11:00-12:00 예약
- **실행역할**: 일반 사용자
- **독립 실행**: 가능
- **기대**: 예약 성공, 응답의 `status`가 `"confirmed"`
MD
git add -A && git commit -q -m "scenarios for booking"

if [ "$mode" = "recheck" ]; then
  cat > docs/test-scenarios/scenarios-review.md <<'MD'
# Test Scenario Review Report

- Source: scenarios-detailed.md
- Date: 2026-11-01

## Summary Verdict
- Overall: NEEDS_WORK

## Findings
### High
- F-1 [S3-04] 내부 리스트 `_bookings` 길이를 단정한다. 관찰 가능한 동작(같은 시간 재예약 Conflict)으로 바꿔야 한다.
- F-2 [AC-3] 취소 후 재예약 시나리오가 없다.
### Medium
- F-3 [S3-05] `status` 필드는 어떤 문서에도 정의되지 않았다.
- F-4 [S3-05] "독립 실행: 가능"인데 S3-01의 예약에 의존한다.
MD
  git add -A && git commit -q -m "review scenarios"
  python3 - <<'PY'
from pathlib import Path
p = Path("docs/test-scenarios/scenarios-detailed.md")
t = p.read_text()
t = t.replace("# Booking Test Scenarios (S3 selected 5 / S2 candidates 9)",
              "# Booking Test Scenarios (S3 selected 6 / S2 candidates 9)")
t = t.replace("### S3-04 예약이 저장된다", "### S3-04 저장된 예약과 같은 시간은 거부된다")
t = t.replace("- **기대**: `rooms._bookings` 길이가 1이다",
              "- **기대**: 같은 10:00-11:00을 다시 예약하면 Conflict")
t += """
### S3-06 취소하면 다시 예약할 수 있다
- **AC-ID**: AC-3
- **진입경로**: 10:00-11:00 예약 → 취소 → 같은 시간 예약
- **실행역할**: 일반 사용자
- **독립 실행**: 가능
- **기대**: 두 번째 예약이 성공한다
"""
p.write_text(t)
PY
  git add -A && git commit -q -m "address review: rewrite S3-04, add S3-06"
fi
echo "built: $dir (${mode:-base})"
