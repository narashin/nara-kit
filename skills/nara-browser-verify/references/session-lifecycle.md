# 세션 생명주기 — 소유권·서버·정리

## 소유권 분류 (상호작용 전에)

- **owned** — 이 run이 만든 browser/context/page/프로세스
- **attached** — 사전에 존재함이 독립적으로 증명된 리소스

**owned만 닫는다.** 소유권을 모르면 닫지 않는다. 알 수 없거나 사용자 소유인 브라우저에 attach하거나 변경하지 않는다.

새 owned Chrome/Chromium은 run-owned isolated profile과 유효한 `--headless=new`를 쓴다. provider launch argument를 증명할 수 없으면 직접 띄운 검증된 endpoint에 attach하거나 `Unverifiable`을 반환한다 — **가시 브라우저로 재시도하지 않는다.**

default user profile, stale port 파일, 이전 browser UUID, `DevToolsActivePort`, tool 이름은 재사용 가능한 세션 근거가 **아니다**. CDP를 쓸 때는 live endpoint·실제 프로세스·port·profile 소유권을 확인한다.

## dev 서버

long-running 서버는 정확한 PID·cwd·명령·port·bounded log 경로를 가진 **run-owned 백그라운드 프로세스**로 시작한다.

- runner가 지원하면 auto-open을 억제한다.
- **프로세스 exit를 기다리지 않는다.** 구체적인 HTTP/port readiness signal을 bounded timeout으로 poll하고, ready 뒤 진행한다.
- 기존 서버 재사용은 cwd가 작업 트리와 일치하고 asset/watch pipeline이 최신이며 bundle·응답이 serving version을 증명할 때만. **cwd만으로는 불충분하다.**
- 다른 작업 트리와 사용자 프로세스를 보존한다. 소유권이나 freshness가 불확실하면 별도 port를 쓴다.

기록할 사실: browser/version, 대상, viewport/DPR, working tree, 서버 프로세스/cwd, serving-version 근거.

## 정리 순서

성공·실패·중단·예외 **모두** 같은 순서로 정리한다.

1. run-created page/tab
2. run-created context
3. run-started browser instance
4. normal shutdown이 실패한 경우에만 정확한 owned 프로세스

강제 종료 전에 프로세스 argument로 PID와 profile을 대조한다. **`killall`·broad `pkill`·task-name bulk kill 금지.** attached browser, 사용자 탭/프로필, 공유 MCP/CDP 인스턴스, 다른 검증 run, 사용자 소유 서버를 보존한다.

정리 잔여물은 application 판정을 바꾸지 않는다 — 사실로만 보고한다.

## 증거 디렉터리

이진 증거는 run-owned `.claude/browser-verify/runs/<ts>/`에 둔다. 부모 태스크가 디렉터리를 지정했으면 그것을 쓴다. **여기에 Markdown 장부를 만들지 않는다** — 판정은 receipt로만 나간다.

- `git check-ignore`로 무시 경로임을 확인한다. 실패하면 **ESCALATE** 후 진행 거부 (인증 흔적이 tracked 파일로 새는 것을 막는다).
- 스크린샷/비디오와 network/HAR/console 인벤토리를 분리한다. Authorization·cookie·token·credential·민감 body가 있으면 그 캡처는 민감으로 분류한다.
- 민감 캡처는 검증된 redaction과 원본·이동 경로 잔여물 부재를 확인한 경우에만 증거로 쓴다. 아니면 소유한 캡처를 안전히 삭제하고 `Unverifiable`을 반환한다.
- 사용자 스크린샷·fixture·profile 등 소유권 불명 산출물을 move/delete하지 않는다.
- 증거 처리를 위해 `.gitignore`를 수정하지 않는다.

## 부모 태스크 handoff

부모(plan의 `검증` 필드, dev-mode verify 단계 등)가 주면 재질문하지 않는다: 정확한 criterion, 대상 URL/환경, headless 요구, auth 전략과 secret-free bootstrap, viewport/state, dev 서버 명령·cwd·readiness, 필요한 스크린샷 증거, 민감 캡처 redaction 규칙, Pass 조건.

빠진 값이 repo 근거로 안전하게 결정 가능하면 채운다. 결과를 바꾸는 **사용자 소유 결정**만 부모에게 돌려보낸다.

중첩 실행의 반환은 다음으로 제한한다 — status, criterion별 사실, 비민감 auth mode, 절대 증거 디렉터리, 검사한 스크린샷 경로, limitation, 정리 사실.
