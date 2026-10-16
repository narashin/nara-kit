# nara-eli5-note — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

실무에서 막힌 것을 5살에게 가르치듯 풀고, 그릴 수 있는 건 HTML/SVG로 그려서, Obsidian vault 관례에 맞춰 노트로 저장함. **ASCII 아트·mermaid는 쓰지 않음** (2026-08-26 결정 — 노트는 글, 그림은 렌더되는 파일).

## 호출

- Claude Code: `/nara-eli5-note [대상] <주제>`
- Codex: `$nara-eli5-note [대상] <주제>`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

대상은 인자에 자연어로 적으면 됨. 플래그 없음.

```
/nara-eli5-note 15살에게 설명하듯 vite tree-shaking 정리해
/nara-eli5-note 매니저 눈높이로 이번 장애 노트로 남겨
/nara-eli5-note 옵시디언에 정리해            ← 대상 없음 → 5살(기본값) 또는 되물음
```

받는 대상: 나이(5·10·15·20~30·40+) / 학년(초등~대학원) / 직군(매니저·엔지니어·디자이너·디렉터·PM·동료) / 관계(배우자·부모·아이·친구). 기본값 5살. 표는 `references/audience.md`.

## 언제 쓰나

- **USE FOR:** "obsidian에 정리해", "옵시디언에 담아", "이거 노트로 남겨", "5살에게 설명하듯 정리해줘", "15살 수준으로 노트 만들어", "공부하게 정리해", "그림으로 정리해줘", "eli5로 노트 써줘", "이거 나중에 볼 수 있게 정리해".
- **DO NOT USE FOR:** 남에게 건넬 설명, PR·diff 설명 (use /nara-explain), 설명만 필요 (use /eli5), 세션 학습을 memory로 (use /nara-retro), 하다 만 일 인계 (use /nara-handoff), Confluence 게시 (use /nara-publish-spec), 아키텍처 결정 (use /nara-adr).

## 기존 스킬과의 자리

| | 설명 | 저장 | 그림 |
| --- | --- | --- | --- |
| `/eli5` | ● 청중별 톤 | ✕ | ✕ |
| `/nara-explain` | ● 남에게 건넬 설명 (PR·diff·온보딩·PM) | ● repo `docs/` | 변경 설명만 HTML |
| `/nara-retro` · `/nara-handoff` | ✕ | ● memory · handoff | ✕ |
| **`/nara-eli5-note`** | ● eli5(청중별) 또는 실무 노트체 | ● Obsidian | ● 필수 (HTML/SVG) |

## 구성

- `SKILL.md` — 절차와 규율 (런타임 로드)
- `references/vault-conventions.md` — vault의 폴더 두 계열·frontmatter 스키마·톤·노트 골격 (설치자 vault 실측 스냅샷 — 자기 vault에 맞게 갱신해서 씀)
- `references/diagram-patterns.md` — HTML/SVG 그림 패턴 8종 + 매체 선택 규칙 + 스타일 베이스 CSS + 의미 고정 색 팔레트
- `references/audience.md` — 대상 4계열 표 + 대상이 바꾸는 것(그림 비중·절 개수·수치 다루는 법) + eli5를 쓰지 말아야 할 대상. `dreambigou/eli5`(MIT) audience 표를 노트 매체에 맞게 고친 것
- `references/formats.md`: 내용 유형(과정, 수치, 메커니즘, 정책, 비교)별로 그림 문서 전체의 진행 형식을 고르는 표. 만져 보기, 동시 재생, 터미널 재현 등 형식별로 지킬 것과 쓰지 않는 형식, 근거가 된 사용자 평가 기록. tiger-kit 작성자의 설명 형식 실험실을 평가 결과로 걸러 다시 쓴 것

## 그림 매체

| 매체 | 언제 | 어떻게 보나 |
| --- | --- | --- |
| HTML 문서 | 기본값. 그림 3개 이상·서로 이어지는 설명, 또는 퀴즈처럼 JS가 필요할 때 | 노트 옆 `<slug>-그림.html`을 `![[...\|-]]` 임베드. Embed HTML 플러그인이 iframe으로 렌더하고 JS가 돎. 높이 토큰 `-`가 없으면 잘림 |
| SVG 단품 | 독립 그림 1~2개이고 JS가 필요 없을 때 | `_assets/`에 두고 `![[...]]` 임베드 |

## 알아둘 것

- **톤을 먼저 묻는다.** eli5냐 실무 노트체냐로 결과물이 크게 갈림. "정리해"만 있으면 되묻게 되어 있음
- **대상은 인자에 있으면 안 물어봄.** 없으면 5살로 감. 매번 되묻지 않는 게 규율에 박혀 있음
- 대상이 엔지니어·대학원이면 eli5 대신 실무 노트체를 권함 — 그 대상에게 비유는 번역 한 겹이 더 붙는 일
- **그림 없는 노트는 실패로 봄.** 정말 그릴 게 없으면 노트에 그 이유를 남김
- `내가 틀렸던 것` 절이 필수 — 기존 vault 노트에서 가장 쓸모 있던 부분이라 규율로 넣었음
- **퀴즈 5문항은 eli5 톤일 때만 자동으로 들어감.** 실무 노트체는 안 넣음(요청하면 넣음). 주제 노트는 그림 HTML에 JS 객체선다, 커리큘럼 노트는 `## 예측 문제` 절 — 후자는 vault의 학습 앱이 간격 반복 카드로 돌리므로 톤과 무관하게 채움
- HTML은 한 파일로 self-contained여야 함. 로컬 이미지 참조는 못 읽으니 `<style>`·마크업·`<script>`를 전부 인라인으로
- **Embed HTML 플러그인이 켜져 있어야 임베드가 렌더됨.** 꺼져 있으면 빈 파일 카드로 떨어지므로 노트에 그 안내를 한 줄 넣음
- vault 구조가 바뀌면 `references/vault-conventions.md`를 갱신함

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
