---
name: webgraph
description: >
  Explore and map website structure into a YAML graph using browser automation
  (playwright-cli). Use when the user invokes /webgraph to explore, crawl, or
  analyze a website's pages and navigation structure.
compatibility: Requires playwright-cli installed and accessible in PATH
allowed-tools: Bash(playwright-cli:*) Read Write Edit Glob
---

# WebGraph - Website Graph Explorer

## Invocation

```
/webgraph <scope> [prompt]
```

- **scope** (required): The exploration scope. Can be:
  - A domain: `example.com`
  - A URL: `https://example.com`
  - A URL with path prefix: `https://example.com/admin`
- **prompt** (optional): Free-form exploration guidance. May include:
  - Login credentials
  - Exploration strategy (e.g. "focus on settings pages", "skip docs")
  - Browser mode preference (`headed` or `headless`)
  - Any other instructions

If no prompt is provided, explore the website broadly with default settings.

## Scope Rules

The scope determines which pages Claude should explore:

- **Domain** (e.g. `example.com`): explore all pages under `https://example.com/*`. Do not follow links to other domains.
- **URL with path** (e.g. `https://example.com/admin`): explore pages under `https://example.com/admin/*`. Pages outside this path prefix are recorded as edges but not explored.
- **Full URL** (e.g. `https://example.com/admin/dashboard`): use this as the starting page; scope is the path prefix `https://example.com/admin/`.

External links encountered during exploration: record them as a note in the source node's `features` or `desc`, but do not navigate to them.

## Exploration Workflow

### 1. Initialize

```bash
# Start a session (use headed by default, unless user specifies headless in prompt)
playwright-cli --session=webgraph open <starting_url> --headed
```

Choose the starting URL from scope:
- If scope is a full URL, use it directly
- If scope is a domain, use `https://<domain>`
- If scope has a path prefix, use it as the starting URL

Create the initial YAML graph file in the current working directory. File naming:
- Extract a clean filename from scope: strip protocol, replace `/` with `-`, remove trailing `-`
- Examples: `example.com.yaml`, `example.com-admin.yaml`

### 2. Explore Pages

For each page:

1. **Snapshot**: Run `playwright-cli --session=webgraph snapshot` to capture the page accessibility tree
2. **Analyze**: Read the snapshot to understand:
   - What this page is (title, type, description)
   - What features/actions are available
   - What data is displayed
   - What links/buttons lead to other pages
3. **Record**: Add or update the node in the YAML graph
4. **Report**: Output a one-line progress update to the user:
   ```
   [Node 3] 用户管理 (list) - https://example.com/admin/users - 发现 4 个子页链接
   ```
5. **Navigate**: Pick the next unvisited link/button to explore. Use `click <ref>` or `goto <url>` to navigate, then repeat.

### 3. Exploration Strategy

- **Breadth-first**: Cover the main navigation structure first (navbar, sidebar, menus), then go deeper.
- **Representative sampling**: For list/detail patterns, explore 1-2 representative detail pages, not every item.
- **Content sites**: For documentation/blog sites, map the category/section structure. Do not crawl every article — record the pattern (e.g. "article detail page") and move on.
- **SPA awareness**: If clicking something changes page content significantly without changing the URL, treat it as a separate node. Use your judgment — tab switches within the same page are not separate nodes, but a modal that represents a full workflow (e.g. "create new item") may warrant its own node.
- **Stop conditions**: Stop when:
  - All discoverable navigation paths within scope have been explored
  - Remaining links are repetitive patterns already covered (e.g. more list items of the same type)
  - The site structure is sufficiently documented

### 4. Error Handling

- **Page load failure**: Try once more. If it still fails, skip the page and note it in the previous node's description.
- **Unexpected dialogs**: Use `dialog-accept` or `dialog-dismiss` as appropriate.
- **Popups/new tabs**: Check `tab-list`, close unwanted tabs with `tab-close`.

### 5. Finalize

When exploration is complete:

1. Update `metadata.summary` with an overall description of the website
2. Update `metadata.explored_at` with the current timestamp
3. Update `metadata.total_pages` with the final node count
4. Close the session:
   ```bash
   playwright-cli --session=webgraph close
   ```
5. Report the final graph file path to the user

## Graph YAML Format

```yaml
metadata:
  scope: "https://example.com/admin"
  summary: "企业后台管理系统，包含用户管理、订单管理、数据看板等模块"
  explored_at: "2026-03-20T15:30:00"
  total_pages: 12

nodes:
  - id: 1
    url: "https://example.com/admin/login"
    title: "登录页"
    type: "auth"
    desc: "管理员登录入口，支持用户名密码登录"
    features:
      - "用户名密码登录"
      - "记住密码选项"
      - "忘记密码链接"
    datas: []

  - id: 2
    url: "https://example.com/admin/dashboard"
    title: "数据看板"
    type: "dashboard"
    desc: "系统主页，展示核心业务指标和快捷入口"
    features:
      - "时间范围筛选"
      - "导出报表"
    datas:
      - "今日订单数/金额"
      - "用户增长趋势图"
      - "TOP5 商品列表"

edges:
  - from: 1
    to: 2
    operation: "输入管理员账号密码后点击'登录'"
  - from: 2
    to: 3
    operation: "点击左侧菜单'用户管理'"
```

### Node Fields

| Field | Type | Description |
|---|---|---|
| `id` | int | Auto-incrementing unique identifier (1, 2, 3...) |
| `url` | string | Page URL |
| `title` | string | Short page title |
| `type` | string | Page type, freely assigned (e.g. home, auth, dashboard, list, detail, form, settings, docs, error, modal) |
| `desc` | string | One-sentence description of the page's purpose |
| `features` | list[string] | Actions/functions available on this page |
| `datas` | list[string] | Data/content displayed on this page |

### Edge Fields

| Field | Type | Description |
|---|---|---|
| `from` | int | Source node ID |
| `to` | int | Target node ID |
| `operation` | string | Natural language description of how to navigate from source to target, including any preconditions |

### Metadata Fields

| Field | Type | Description |
|---|---|---|
| `scope` | string | The exploration scope as provided by the user |
| `summary` | string | Overall description of the website (filled at the end) |
| `explored_at` | string | ISO 8601 timestamp of exploration completion |
| `total_pages` | int | Total number of nodes in the graph |

## Real-time Graph Updates

Update the YAML file after each page exploration. This means:
- After analyzing a new page, append the node to `nodes` and any new edges to `edges`
- Update `metadata.total_pages`
- Use the Edit tool to modify the existing file — do NOT rewrite the entire file each time

## Login Handling

If the user provides credentials in the prompt:
1. Navigate to the login page
2. Use `snapshot` to find the input fields
3. Use `fill <ref> <text>` to enter credentials
4. Use `click <ref>` to submit
5. Continue exploration after successful login

If no credentials are provided and a login wall is encountered:
- Record the login page as a node
- Note in the node description that authentication is required
- Explore only publicly accessible pages

## playwright-cli Reference

See [references/playwright-commands.md](references/playwright-commands.md) for the full command reference.

Key patterns:
- Always use `--session=webgraph` for all commands
- Run `snapshot` before any interaction to get element `[ref=xxx]` values
- After navigation or interaction, run `snapshot` again to see updated state
- Use `goto <url>` for direct URL navigation, `click <ref>` for in-page navigation

## Gotchas

- **Always snapshot before interacting**: You need `[ref=xxx]` values from snapshot output to use `click`, `fill`, etc.
- **Session cleanup**: Always close the session when done, even if exploration fails midway.
- **Large snapshots**: Some pages produce very long snapshots. Focus on extracting structural information (navigation, forms, data tables) rather than reading every text node.
- **Infinite scroll / pagination**: Note the pattern exists, explore 1-2 pages of results, then move on.
- **URL fragments and query params**: Pages like `/users?page=2` and `/users?page=3` are the same node type — don't create separate nodes for pagination.
- **Redirects**: If `goto` redirects to a different URL, use the final URL as the node's URL.
- **File naming special characters**: When converting scope to filename, replace `://` with empty, `/` with `-`, remove trailing `-`, and strip `?`, `#`, `&`, `=` and everything after them.
