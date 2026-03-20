# playwright-cli Command Reference

All commands use the format: `playwright-cli --session=<name> <command> [args] [options]`

Add `--headed` to show the browser window. Add `--browser <name>` to choose browser (chrome/firefox/webkit).

## Navigation

| Command | Description |
|---|---|
| `open [url]` | Open browser (optionally navigate to url) |
| `goto <url>` | Navigate to a url |
| `go-back` | Go back to the previous page |
| `go-forward` | Go forward to the next page |
| `reload` | Reload the current page |

## Snapshot & Inspection

| Command | Description |
|---|---|
| `snapshot` | Capture page accessibility tree snapshot. Returns elements with `[ref=xxx]` attributes for interaction. |
| `screenshot [ref]` | Screenshot of current page or specific element |
| `console [min-level]` | List console messages |
| `network` | List all network requests since page load |

## Interaction

| Command | Description |
|---|---|
| `click <ref>` | Click an element by ref |
| `dblclick <ref>` | Double click an element |
| `type <text>` | Type text into focused editable element |
| `fill <ref> <text>` | Fill text into a specific editable element |
| `select <ref> <val>` | Select an option in a dropdown |
| `check <ref>` | Check a checkbox or radio button |
| `uncheck <ref>` | Uncheck a checkbox or radio button |
| `hover <ref>` | Hover over element |
| `drag <startRef> <endRef>` | Drag and drop between two elements |
| `upload <file>` | Upload file(s) |

## Keyboard

| Command | Description |
|---|---|
| `press <key>` | Press a key (e.g. `Enter`, `Tab`, `ArrowDown`) |
| `keydown <key>` | Press key down |
| `keyup <key>` | Release key |

## Dialog

| Command | Description |
|---|---|
| `dialog-accept [prompt]` | Accept a dialog (alert/confirm/prompt) |
| `dialog-dismiss` | Dismiss a dialog |

## Tab Management

| Command | Description |
|---|---|
| `tab-list` | List all tabs |
| `tab-new [url]` | Create a new tab (optionally navigate to url) |
| `tab-close [index]` | Close a tab |
| `tab-select <index>` | Switch to a tab by index |

## Session Management

| Command | Description |
|---|---|
| `list` | List all browser sessions |
| `close` | Close current browser session |
| `close-all` | Close all sessions |
| `kill-all` | Force kill all sessions (for zombie processes) |

## Storage & Authentication

| Command | Description |
|---|---|
| `state-save [filename]` | Save authentication state to file |
| `state-load <filename>` | Load authentication state from file |
| `cookie-list` | List all cookies |
| `cookie-get <name>` | Get a cookie by name |
| `cookie-set <name> <value>` | Set a cookie |
| `cookie-delete <name>` | Delete a cookie |
| `cookie-clear` | Clear all cookies |

## Workflow Notes

- Always use `--session=<name>` to maintain browser state across commands
- Use `snapshot` to get element refs before `click`/`fill`/`select` interactions
- The snapshot returns an accessibility tree. Elements have `[ref=xxx]` attributes used for interaction commands.
- After `click` or navigation, call `snapshot` again to see the updated page state
- Use `state-save`/`state-load` to persist login sessions across explorations
