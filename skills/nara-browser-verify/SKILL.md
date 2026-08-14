---
name: nara-browser-verify
description: >-
  Judge browser-visible acceptance criteria in a headless runtime, returning a per-axis verdict backed by runtime evidence.
  USE FOR: "브라우저 AC 검증", "이 화면 AC 통과했나", "런타임으로 확인해줘", "headless 검증", "browser-verify", dev-mode verify step for browser-visible AC.
  DO NOT USE FOR: env↔local 비교 (→ nara-ui-diff), 스샷 캡처 (→ nara-local-shot), 테스트 코드 작성 (→ nara-test-implement), 코드 AC 갭 분석 (→ nara-gap).
---

# browser-verify — 브라우저 AC 런타임 검증

승인된 **browser-visible AC**만 헤드리스 런타임에서 판정한다. 읽기 전용 verifier — 소스·커밋·원격 상태를 수정하지 않는다. `nara-ui-diff`와 달리 baseline 없이 **criterion 대비 판정**만 하므로, 결론은 후보가 아니라 `Pass | Fail | Blocked | Unverifiable`이다.

## Core Rules

1. **증거 없으면 Pass 없음** — 축별 필수 증거는 [evidence-matrix](references/evidence-matrix.md). 한 축이라도 필수 증거가 없으면 그 축 `Unverifiable`, **aggregate `Pass` 금지**.
2. **컨닝 금지** — `element.click()` / `form.submit()` / `dispatchEvent()`는 상호작용 증거가 **아니다**. trusted pointer/keyboard API만. 상세 [anti-cheat](references/anti-cheat.md).
3. **headless-only** — 가시 브라우저 fallback 없음. 안전한 헤드리스 인증을 못 세우면 `Unverifiable` 반환.
4. **자기 소유만 정리** — run-owned만 종료. `killall`·broad `pkill` 금지. [session-lifecycle](references/session-lifecycle.md).
5. **크레덴셜 격리** — 비밀값을 응답·아티팩트·로그·스크린샷 어디에도 남기지 않는다. 기록은 `auth mode: token-headless` 같은 비민감 사실만. 증거 디렉터리는 **반드시 `git check-ignore`를 통과**해야 하며, 경로 선택은 [session-lifecycle](references/session-lifecycle.md#증거-디렉터리) 사다리를 따른다(무시되는 경로를 하나도 못 찾으면 그때 ESCALATE).
6. **차이·관련값만 인라인** — full computed dump·HAR·콘솔 전량은 디스크 아티팩트. 채팅 인라인 금지.
7. **receipt 먼저 → 중단** — 자동 수정·자동 체이닝 없음. 실패 축은 보고만.

## 인자 ($ARGUMENTS)

`nara-browser-verify [--ac <id|파일>] [--url <target>] [--viewport <WxHxDPR>] [--driver <auto|chrome-devtools|playwright>] [--dry-run]`

인자가 없으면 자동 감지: `docs/plan.md`의 `검증` 필드 → `docs/requirements.md`의 `browser-visible: yes` AC → 그래도 없으면 `Blocked`(대상 미확정). 있는 신호로 공급 가능한 값은 플래그로 강제하지 않는다.

## Step 0 — override + profile

```bash
test -f .claude/overrides/browser-verify.md && cat .claude/overrides/browser-verify.md   # add/raise/narrow only
```

제품값(대상 URL·dev 명령·로그인 경로)은 **소비 repo**가 소유한다. `.claude/ui-diff/env.md`가 있으면 재사용, 없으면 부모 태스크(plan/AC)가 준 값. user-global provisioning 금지.

## Procedure

1. **Scope** — criterion·대상·viewport·승인된 상호작용 경계를 고정. 미해결이면 `Blocked`(사용자 결정) 또는 `Unverifiable`(안전한 검증 경로 없음)로 **실행 전에** 정지.
2. **환경** — 새 의존성 설치 없이 드라이버 선택. 사다리는 [../nara-ui-diff/references/drivers.md](../nara-ui-diff/references/drivers.md) (같이 설치된 스킬 파일 참조 — 없으면 chrome-devtools MCP 기본으로 진행). 새 Chrome 프로세스는 `--headless=new`와 run-owned `user-data-dir`를 증명한다.
3. **서버** — dev 서버가 필요하면 이 스킬이 기동·readiness·정리를 소유한다. repo의 dev 명령을 run-owned 백그라운드로 띄우고, **프로세스 exit 대기 금지** — HTTP/port readiness를 bounded timeout으로 poll. 상세 [session-lifecycle](references/session-lifecycle.md).
4. **인증** — 우선순위: 인증 불필요 → run-owned 검증된 세션 재사용 → repo가 지원하는 header/cookie/storage bootstrap → OTP·MFA·SSO·CAPTCHA 없는 완전 비대화형 로그인. 메커니즘은 [../nara-local-shot/references/auth-bypass.md](../nara-local-shot/references/auth-bypass.md) (없으면 repo 근거로 판단, 추측 금지). 주입 방식을 지어내지 않는다. 못 세우면 `Unverifiable`.
5. **검증** — 알려진 초기 상태에서 시작해 criterion이 요구하는 상호작용과 최종 상태를 관찰. 결정에 관련된 최종 상태마다 run-owned 스크린샷을 최소 1장 남기고 **실제로 열어본다**.
6. **판정** — criterion을 축에 매핑하고 축마다 `Pass|Fail|Unverifiable`. 미검사 축은 Pass로 올리지 않는다.
7. **정리** — run-created page → context → browser 순. 잔여물은 판정을 바꾸지 않고 사실로 보고.

## Output (receipt)

```
브라우저 AC 검증 완료 (recorded only).
- criterion: `<id 또는 한 줄>` · driver: `chrome-devtools` · viewport: `<WxHxDPR>` · auth mode: `token-headless`
- 축 판정: geometry ✅ / content ✅ / asset ⚠️ Unverifiable(스크린샷 없음) / behavior ❌ (기대 request 없음)
- side effects: browser 1 runtime opened (`<target host>`), dev server run-owned PID `<n>` 종료, 0 writes to app
- artifact: `.claude/browser-verify/runs/<ts>/` (스크린샷 N장, network log)
- Status: Unverifiable
```

마지막 줄은 정확히 하나의 terminal token — `Status: Pass | Fail | Blocked | Unverifiable`. `--dry-run`이면 브라우저를 열지 않고 계획만, status `skipped`.

## Examples

**AC**: "티켓 저장 버튼을 누르면 목록에 새 행이 보인다"

```text
behavior  → trusted click(uid) → POST /api/tickets 201 관찰 → 목록 재렌더 확인   ✅ Pass
content   → 새 행의 제목·상태 텍스트가 입력값과 일치                              ✅ Pass
asset     → criterion 범위 밖                                                    해당 없음
Status: Pass
```

같은 AC인데 스크린샷을 못 남겼다면 `behavior`는 Pass여도 시각 축이 걸린 경우 그 축은 `Unverifiable`이고 aggregate는 `Pass`가 아니다. `element.click()`으로 눌렀다면 behavior 축 자체가 증거 없음 → `Unverifiable`.

## Error Handling (if-then)

| 트리거 | 대응 |
|---|---|
| criterion·대상 미확정 | 실행 전 `Blocked` — 브라우저 열지 않음 |
| 안전한 헤드리스 인증 불가 (OTP/MFA/SSO/CAPTCHA 요구) | `Unverifiable` — 가시 브라우저로 우회 금지 |
| MCP 드라이버 하나도 없음 | `Unverifiable: requires live runtime` — 정적 분석으로 대체 금지 |
| 스크린샷 없음·비었음·열기 실패 | 그 축 `Unverifiable`, aggregate `Pass` 금지 |
| `evaluate_script`가 `{}` 반환 | 측정 실패로 처리 — 직렬화 규율 적용 후 재시도 ([anti-cheat](references/anti-cheat.md)) |
| 증거 디렉터리가 gitignore 안 됨 | `→ ESCALATE:` 후 진행 거부 |
| dev 서버 readiness timeout | run-owned 프로세스 정리 후 `Blocked` + 로그 경로 보고 |
| 정리 중 잔여물 발견 | 판정 변경 없이 사실로 보고 |
| 그 외 실패 | `❌ 실패:` 블록 |

## Hallucination & Safety Guards

- 관찰하지 않은 값·selector·URL 창작 금지. 측정 안 한 것은 `[UNVERIFIED]`. 임의 pixel tolerance 발명 금지 — 명백한 mismatch만 보고하고 미세차는 `Unverifiable`.
- 결제·외부 통신·비가역 삭제·production 데이터 변경·권한 변경 금지. 승인된 UI 상태는 실제 전송보다 repo 근거 기반 response mock 우선.
- 검증을 위해 제품 소스를 수정하지 않는다. 런타임 전용 mock은 label하고 제거한다.
- MCP 드라이버가 하나도 없으면 정적 분석으로 대체하지 않는다 — 판정 스킬이라 정적 근거로 `Pass`를 낼 수 없다. 워크플로 스파인 밖 단독 호출 가능(NL/slash 트리거만).

## References

- [evidence-matrix.md](references/evidence-matrix.md) — 축별 필수 증거 + 7축 verbatim 비교
- [anti-cheat.md](references/anti-cheat.md) — trusted input·mutation·모션·필드 비우기·직렬화 규율
- [session-lifecycle.md](references/session-lifecycle.md) — 소유권 분류·서버 readiness·정리 순서·증거 디렉터리
