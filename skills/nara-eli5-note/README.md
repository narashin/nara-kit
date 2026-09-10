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
/nara-eli5-note 매니저한테 설명하듯 이번 장애 노트로 남겨
/nara-eli5-note 옵시디언에 정리해            ← 대상 없음 → 5살(기본값) 또는 되물음
```

받는 대상: 나이(5·10·15·20~30·40+) / 학년(초등~대학원) / 직군(매니저·엔지니어·디자이너·디렉터·PM·동료) / 관계(배우자·부모·아이·친구). 기본값 5살. 표는 `references/audience.md`.

## 언제 쓰나

- **USE FOR:** "obsidian에 정리해", "옵시디언에 담아", "이거 노트로 남겨", "5살에게 설명하듯 정리해줘", "15살 수준으로 노트 만들어", "매니저한테 설명하듯 정리해", "그림으로 정리해줘", "eli5로 노트 써줘".
- **DO NOT USE FOR:** 설명만 필요 (use /eli5), 세션 학습을 memory·handoff로 (use /nara-reflect), Confluence 게시 (use /nara-publish-spec), 아키텍처 결정 (use /nara-adr).

## 기존 스킬과의 자리

| | 설명 | 저장 | 그림 |
| --- | --- | --- | --- |
| `/eli5` | ● 청중별 톤 | ✕ | ✕ |
| `/nara-reflect` | ✕ | ● memory·handoff | ✕ |
| **`/nara-eli5-note`** | ● eli5(청중별) 또는 실무 노트체 | ● Obsidian | ● 필수 (HTML/SVG) |

## 구성

- `SKILL.md` — 절차와 규율 (런타임 로드)
- `references/vault-conventions.md` — vault의 폴더 두 계열·frontmatter 스키마·톤·노트 골격 (설치자 vault 실측 스냅샷 — 자기 vault에 맞게 갱신해서 씀)
- `references/diagram-patterns.md` — HTML/SVG 그림 패턴 8종 + 매체 선택 규칙 + 스타일 베이스 CSS + 의미 고정 색 팔레트
- `references/audience.md` — 대상 4계열 표 + 대상이 바꾸는 것(그림 비중·절 개수·수치 다루는 법) + eli5를 쓰지 말아야 할 대상. `dreambigou/eli5`(MIT) audience 표를 노트 매체에 맞게 고친 것

## 그림 매체

| 매체 | 언제 | 어떻게 보나 |
| --- | --- | --- |
| HTML 문서 | 그림 3개 이상·서로 이어지는 설명 (기본값) | 노트 옆 `<slug>-그림.html`, HTML Reader류 플러그인으로 클릭해서 엶 (임베드 미지원) |
| SVG 단품 | 독립 그림 1~2개 | `_assets/`에 두고 `![[...]]` — 노트 안에 바로 렌더됨 |

## 알아둘 것

- **톤을 먼저 묻는다.** eli5냐 실무 노트체냐로 결과물이 크게 갈림. "정리해"만 있으면 되묻게 되어 있음
- **대상은 인자에 있으면 안 물어봄.** 없으면 5살로 감. 매번 되묻지 않는 게 규율에 박혀 있음
- 대상이 엔지니어·대학원이면 eli5 대신 실무 노트체를 권함 — 그 대상에게 비유는 번역 한 겹이 더 붙는 일
- **그림 없는 노트는 실패로 봄.** 정말 그릴 게 없으면 노트에 그 이유를 남김
- `내가 틀렸던 것` 절이 필수 — 기존 vault 노트에서 가장 쓸모 있던 부분이라 규율로 넣었음
- HTML은 self-contained여야 함 — 뷰어 플러그인이 스크립트·로컬 이미지 참조를 막음. `<style>` + 순수 마크업만
- vault 구조가 바뀌면 `references/vault-conventions.md`를 갱신함

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
