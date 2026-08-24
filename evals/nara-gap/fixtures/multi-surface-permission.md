# requirements.md (excerpt)

- [ ] FR-7: A co-editor MUST be able to edit a resource but MUST NOT be able to
  delete it. (permission / authorization)

# Codebase state digest (what inspection found)

- Backend: `DELETE /resources/{id}` guarded by `require_primary_owner` →
  co-editor receives 403. (server enforcement present)
- Backend list serializer emits a `can_delete` flag = primary-owner OR admin.
- Frontend list: delete button gated on `can_delete` (co-editor: hidden).
  Edit button gated on `can_edit` (co-editor: shown). (client gating present)
- Tests: `test_co_editor_cannot_delete` covers the BACKEND guard only.
  No client-layer gating test. No test asserting the flag semantics
  (that a co-editor gets can_edit=true and can_delete=false).
