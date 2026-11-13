# nara-flow-map — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

시스템 흐름 하나를 애니메이션 지도 HTML 한 장으로 만든다. 상자를 공간에 배치하고, 이름표 카드가 선을 따라 날아가고, 저장소에 줄이 쌓이고, 규칙 칸이 통과하거나 멈추고, 아직 없는 상자는 흐리게 보인다. 단계 타임라인으로 아무 단계로나 건너뛸 수 있다.

## 호출

- Claude Code: `/nara-flow-map`
- Codex: `$nara-flow-map`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "흐름 애니메이션", "애니메이션 지도", "데이터 흐름 지도", "흐름을 지도로 보여줘", "데이터가 어디로 가는지 움직이게 보여줘", "flow map", "flow animation", "flow-map".
- 순서: 사실 수집(코드·문서 근거만, 못 본 것은 `[미확인]`) → 구성안 고르기(지도 / 주인공 카드 / 장면별, 미리보기) → 데이터 블록 작성 → 자동 검사 → (선택) 영상.
- 영상: 페이지의 "● 영상으로 저장" 버튼으로 보는 사람이 webm을 직접 받거나, `assets/record_flow_map.mjs`로 mp4를 만든다(이미 설치된 playwright-core·ffmpeg만 사용).
- 결과는 `docs/explain/<흐름-이름>-flow-map.html`. 엔진은 `assets/flow-map.html`에 고정이고 데이터 블록만 바뀐다.
- 보여 주기 전에 페이지 안의 `flowSelfCheck()`가 통과해야 한다. 처음부터 끝까지 재생 오류, 단계 점프 후 상태 복원, 선이 상자를 지나가는지, 선 끝이 상자에 닿는지, 카메라가 상자를 자르는지를 본다.
- **DO NOT USE FOR:** 참여자끼리 주고받는 순서를 학습 노트로 (→ nara-eli5-note 스텝 재생기), 상태별 갈래와 결말 (→ nara-eli5-note 상태 지도 재생기), 대상별 설명 문서·PR 설명 (→ nara-explain), 모듈·import 구조 지도, 영상 파일만 필요할 때.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
- 엔진 계약: [references/engine.md](references/engine.md)
