# UniC Demo Project

This is a ready-to-use demo project for **Universal i18n Commander (UniC)**.  
Load it to see how UniC detects key statuses (OK / GHOST / DUP) across different plugin patterns.

---

## How to load this demo in UniC

1. Open UniC
2. Go to **Project Settings**
3. Set the following paths:

| Field | Value |
|---|---|
| **Master JSON** | `tests/demo_project/lang/master.json` |
| **Target JSON** | `tests/demo_project/lang/pl.json` |
| **Source directory** | `tests/demo_project/src/` |
| **Extensions** | `.py,.jsx,.vue` |

4. Click **Load & Initialize Project**
5. Select a plugin from the dropdown and click **SCAN**

---

## What's inside

### `lang/`
| File | Description |
|---|---|
| `master.json` | 14 keys covering all expected statuses |
| `pl.json` | Polish translation — contains 2 intentional duplicate values |

### `src/`
| File | Plugin to use | Patterns covered |
|---|---|---|
| `main_app.py` | `Python — T.get / self.T.get` | `T.get("key")`, `self.T.get("key")`, `self._t("key")` |
| `utils.py` | `Python — _() / gettext()` | `_("key")`, `gettext("key")` |
| `Component.jsx` | `JavaScript — t() / i18n.t()` | `t("key")`, `i18n.t("key")` |
| `MyView.vue` | `JavaScript — $t() [Vue]` | `{{ $t("key") }}` |
| `submodule/widget.py` | `Python — T.get / self.T.get` | tests recursive subdirectory scanning |

---

## Expected results

For detailed per-plugin expected output see [`../EXPECTED.md`](../EXPECTED.md).

### Quick reference

| Key | Expected status | Reason |
|---|---|---|
| `KEY_OK_*` | 🔵 OK | found in source by matching plugin |
| `KEY_DUP_A` / `KEY_DUP_B` | 🔴 DUP | both have identical value in `pl.json` |
| `KEY_GHOST_NEVER_USED` | 🟠 GHOST | not present anywhere in source files |
| `KEY_GHOST_COMMENT_ONLY` | 🟠 GHOST | appears only inside a code comment |
| `KEY_GHOST_STRING_LITERAL` | 🟠 GHOST | appears as a plain string, not inside a translation call |

> **Note:** `KEY_GHOST_COMMENT_ONLY` may appear as 🔵 OK with `_()` and `t()` plugins —
> this is a known limitation of regex-based scanning. Comments are not excluded from matching.

---

## Plugin selection guide

Not sure which plugin to pick for your project? Match by what your code looks like:

| Your code | Plugin to select |
|---|---|
| `T.get("key")` or `self.T.get("key")` | `Python — T.get / self.T.get` |
| `self._t("key")` or `self.ui.get("key")` | `Python — self._t / self.ui.get` |
| `_("key")` or `gettext("key")` | `Python — _() / gettext()` |
| any of the above mixed | `Python — all patterns` |
| `t("key")` or `i18n.t("key")` | `JavaScript — t() / i18n.t()` |
| `{{ $t("key") }}` | `JavaScript — $t() [Vue]` |
