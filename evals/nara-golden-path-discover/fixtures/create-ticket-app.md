# App state for `/create-ticket` (already captured; no repo in this run)

## docs/test-scenarios/scenarios-detailed.md (nara-test-discover E2E decomposition)

- E2E-1 (Happy): 로그인한 사용자가 `/create-ticket`에서 제목·우선순위를 입력하고 제출하면 `/tickets/<id>`로 이동하고 토스트 "티켓이 생성되었습니다"가 보인다.
- E2E-2 (Error): 제목 없이 제출하면 제목 필드 아래 "제목을 입력하세요"가 보이고 이동하지 않는다.
- E2E-3 (Edge): 같은 제목으로 두 번 제출하면 두 번째에 "이미 같은 제목의 티켓이 있습니다" 경고가 뜬다(서버 409).

## src/app/create-ticket/page.tsx

```tsx
export default function CreateTicketPage() {
  return (
    <form data-testid="create-ticket-form" onSubmit={submit}>
      <label htmlFor="title">제목</label>
      <input id="title" name="title" />
      <select name="priority" aria-label="우선순위">
        <option value="low">낮음</option><option value="high">높음</option>
      </select>
      <button type="submit">생성</button>
    </form>
  );
}
```

## Environment

- Base URL `http://localhost:3000`, auth via saved storage state `e2e/.auth/user.json`.
- Tests run with `workers: 4`; tickets are shared across workers (no per-worker isolation yet).
