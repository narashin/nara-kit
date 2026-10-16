---
defaults:
  assignee: currentUser()
  mention: 00000000-0000-0000-0000-000000000000
  ready_statuses: [To Do, Selected for Development]
  mirror_statuses: [In Progress, In Review]
  misc_session_group: nara-kit
profiles:
  - jira_project: PROJ
    pr_language: en
    repos:
      fe: { repo: acme-sre/web-ui,     git_host: git.example.com, session_group: web-ui,     local_path: "" }
      be: { repo: acme-sre/api-server, git_host: git.example.com, session_group: api-server, local_path: "" }
  - jira_project: OPS
    pr_language: ko
    repos:
      default: { repo: acme-sre/sandbox-dns, git_host: git.example.com, session_group: sandbox-dns, local_path: "" }
---
