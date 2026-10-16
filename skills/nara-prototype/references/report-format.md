# REPORT.md 골격

저장 위치는 `docs/prototypes/<slug>/REPORT.md`다. 절 순서는 아래와 같이 고정이고, 내용이 없는 절은 뺀다. 판정 상태는 그 상태를 소유한 절에 한 번만 쓴다. 결정이 앞에 오고 명령 세부는 뒤에 온다.

| 절 | 소유하는 것 |
|---|---|
| `## Confirmed` | 증거가 붙은 결론. 변형을 비교하면 표, 결론이 하나면 문장 하나 |
| `## Production implication` | 버릴지, 다시 돌릴지, 실제 구현으로 넘길지와 다음 결정 |
| `## Tested` | 실행마다 영수증 하나 |
| `## Variants or harness` | 변형·harness 경로, 실행 URL, 바꾼 차원, 정리 후 `kept \| removed` |
| `## Still fake` | 연동별 fake/real과 검증하지 못한 범위 |

마지막 줄은 `verdict: <Pass | Fail | Blocked | Unverifiable>` 하나다.

## 판정 4종

| 판정 | 뜻 |
|---|---|
| `Pass` | 모든 기준을 실행 증거로 확인했고, 질문에 답이 났다 |
| `Fail` | 실행은 됐고, 기준 중 하나 이상을 증거상 넘지 못했다 |
| `Blocked` | 환경, 의존성, 경로 무시 설정, 범위 확장 때문에 실행하지 못했다. 사람이 풀어야 진행된다 |
| `Unverifiable` | 실행은 됐지만 기준을 판정할 증거(출력, 스크린샷, runtime 확인)가 없다 |

## Confirmed 표

변형을 비교할 때 헤더는 정확히 아래와 같다. 3번째 변형이 있으면 `B` 뒤에 `C` 열을 더한다.

```
| Criterion | A | B | Conclusion | Evidence |
|---|---|---|---|---|
```

칸 값은 관찰한 값이다. 차이가 관찰되지 않았으면 `not observed`, 증거가 없으면 `unverifiable`로 적는다. 표 아래 한 줄로 변형 사이에 내용·데이터·상태가 같았는지 적는다. 미적 선호는 행으로 올리지 않는다.

## Tested 영수증

실행 한 번마다 아래 필드를 그대로 채운다. 요약하지 않고 실행한 값을 적는다.

```
Command: <실행한 명령과 인자 그대로>
CWD: <절대 경로>
Exit code: <정수>
Output: <짧은 요약 또는 출력 파일 절대 경로>
Artifact: <절대 경로 | none>; ownership: run-owned | pre-existing
Screenshot: <절대 경로 | N/A>; inspected: yes | no | N/A
```

## 예시 (placeholder)

````markdown
# 검색창 debounce 방식 비교 (PROJ-123)

## Confirmed

| Criterion | A (leading 300ms) | B (trailing 300ms) | Conclusion | Evidence |
|---|---|---|---|---|
| "acme" 입력 시 요청 수 1회 이하 | 2회 | 1회 | B 충족 | `docs/prototypes/search-debounce/out/run-2.txt` |
| 마지막 입력 반영 | 누락 1회 | 반영 | B 충족 | `docs/prototypes/search-debounce/out/run-2.txt` |
| 첫 결과까지 지연 700ms 이하 | 40ms | 340ms | 둘 다 충족 | `docs/prototypes/search-debounce/out/run-3.txt` |

입력 시퀀스와 fake 응답은 두 변형에서 같았다.

## Production implication

B를 채택 후보로 둔다. 실제 구현은 web-ui의 검색 훅에서 `/nara-implement`로 진행한다. 프로토타입 코드는 옮기지 않는다.

## Tested

```
Command: node docs/prototypes/search-debounce/harness.mjs --variant all
CWD: /work/web-ui
Exit code: 0
Output: /work/web-ui/docs/prototypes/search-debounce/out/run-2.txt
Artifact: /work/web-ui/docs/prototypes/search-debounce/harness.mjs; ownership: run-owned
Screenshot: N/A; inspected: N/A
```

## Variants or harness

- harness: `docs/prototypes/search-debounce/harness.mjs` (바꾼 차원: debounce 가장자리만) · removed
- 리포트: `docs/prototypes/search-debounce/REPORT.md` · kept

## Still fake

- 검색 API: fake (고정 지연 20ms 응답). 실제 서버 지연은 검증 안 함

verdict: Pass
````
