# Confluence Storage Format Conversion Rules

**CRITICAL: `content_format: "storage"` 사용. markdown 아님.**

Confluence는 자체 storage format (XHTML + Atlassian macro)을 사용한다. markdown으로 올리면 테이블, 코드블록 등이 깨진다.

## Conversion Rules

**Headings:**
```
## 1. Background  →  <h1>1. Background</h1>
### Current Behavior  →  <h3>Current Behavior</h3>
```

**Lists (bullet):**
```html
<ul style="list-style-type: square;">
  <li>item 1</li>
  <li>item 2</li>
</ul>
```

**Lists (ordered):**
```html
<ol>
  <li>item 1</li>
  <li>item 2</li>
</ol>
```

**Tables:**
```html
<table class="wrapped">
  <colgroup><col/><col/></colgroup>
  <tbody>
    <tr><th scope="col">Header 1</th><th scope="col">Header 2</th></tr>
    <tr><td>val 1</td><td>val 2</td></tr>
  </tbody>
</table>
```

**Code blocks:**
```html
<ac:structured-macro ac:name="code" ac:schema-version="1">
  <ac:parameter ac:name="language">typescript</ac:parameter>
  <ac:plain-text-body><![CDATA[const x = 1;]]></ac:plain-text-body>
</ac:structured-macro>
```

**Bold / Inline code:**
```html
<strong>bold text</strong>
<code>inline code</code>
```

**Jira ticket link macro:**
```html
<ac:structured-macro ac:name="jira" ac:schema-version="1">
  <ac:parameter ac:name="server">Jira</ac:parameter>
  <ac:parameter ac:name="serverId">fd8fda8e-f52c-3c30-9024-3257ba6f1611</ac:parameter>
  <ac:parameter ac:name="key">LYRIS-XXX</ac:parameter>
</ac:structured-macro>
```

**Line break:** `<br/>`
**Paragraph:** `<p>text</p>`
**Empty line:** `<p><br/></p>`

**Reference (LYRIS-337 page):** 실제 팀 페이지의 storage format을 `confluence_get_page(convert_to_markdown=false)`로 조회하여 패턴을 따를 것.

## MCP API Call

```
mcp__confluence__confluence_create_page(
  space_key: "<space>",
  title: "LYRIS-XXX 설명",
  content: "<Confluence storage format XHTML>",
  content_format: "storage",
  parent_id: "<parent page ID>"
)
```

**MCP 미연결 시:** REST API fallback 또는 XHTML 로컬 export
