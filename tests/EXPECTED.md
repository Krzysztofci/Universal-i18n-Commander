# EXPECTED.md — Oczekiwane wyniki testów UniC

Zestaw testowy dla Universal i18n Commander.
Katalog projektu: `unic_test_suite/`
Master JSON: `lang/master.json`
Katalog źródeł: `src/`
Rozszerzenia: `.py,.jsx,.vue`

---

## Legenda statusów

| Kolor | Status | Znaczenie |
|-------|--------|-----------|
| 🔵 Niebieski | **OK** | Klucz znaleziony w kodzie przez aktywny plugin |
| 🔴 Czerwony | **DUP** | Dwa lub więcej kluczy mają tę SAMĄ wartość w tłumaczeniu |
| 🟠 Pomarańczowy | **GHOST** | Klucz istnieje w JSON ale NIE znaleziony przez aktywny plugin |

> WAŻNE: Status zależy od aktywnego pluginu. Ten sam klucz może być OK
> przy jednym pluginie i GHOST przy innym — to jest POPRAWNE zachowanie.

---

## Oczekiwane wyniki według pluginu

### Plugin: `dict_get` — wzorzec `T.get("key")` / `self.T.get("key")`

Regex: `(?:\bself\.T|\bT)\.get\(\s*["']([^"']+)["']`

Pliki skanowane: `src/main_app.py`, `src/submodule/widget.py`

| Klucz | Oczekiwany status | Plik źródłowy | Uwaga |
|-------|------------------|---------------|-------|
| KEY_OK_DICT_GET | 🔵 OK | main_app.py L17 | `T.get("KEY_OK_DICT_GET", ...)` |
| KEY_OK_DOUBLE_QUOTE | 🔵 OK | main_app.py L18 | `self.T.get("KEY_OK_DOUBLE_QUOTE", ...)` |
| KEY_OK_SINGLE_QUOTE | 🔵 OK | main_app.py L21 | `T.get('KEY_OK_SINGLE_QUOTE', ...)` |
| KEY_OK_MULTILINE | 🔵 OK | main_app.py L24 | `T.get(\n"KEY_OK_MULTILINE",...)` — UWAGA: regex musi działać bez DOTALL |
| KEY_DUP_A | 🔴 DUP | main_app.py L29 | wartość w pl.json = "DUPLIKAT — ta sama wartość" |
| KEY_DUP_B | 🔴 DUP | main_app.py L30 | wartość w pl.json = "DUPLIKAT — ta sama wartość" |
| KEY_OK_SUBDIR | 🔵 OK | submodule/widget.py L14 | test rekurencji podkatalogu |
| KEY_OK_SELF_T | 🟠 GHOST | — | ten plugin nie łapie `self._t("...")` |
| KEY_OK_UNDERSCORE | 🟠 GHOST | — | ten plugin nie łapie `_("...")` |
| KEY_OK_T_FN | 🟠 GHOST | — | ten plugin nie łapie `t("...")` |
| KEY_OK_DOLLAR_T | 🟠 GHOST | — | ten plugin nie łapie `$t("...")` |
| KEY_GHOST_NEVER_USED | 🟠 GHOST | — | nie ma nigdzie w kodzie |
| KEY_GHOST_COMMENT_ONLY | 🟠 GHOST | — | jest tylko w komentarzu `# KEY_GHOST...` |
| KEY_GHOST_STRING_LITERAL | 🟠 GHOST | — | jest jako `plain = "KEY_GHOST..."` ale nie w T.get() |

---

### Plugin: `self_t` — wzorzec `self._t("key")` / `self.ui.get("key")`

Regex: `(?:self\._t|self\.ui\.get)\(\s*["']([^"']+)["']`

Pliki skanowane: `src/main_app.py`

| Klucz | Oczekiwany status | Uwaga |
|-------|------------------|-------|
| KEY_OK_SELF_T | 🔵 OK | `self._t("KEY_OK_SELF_T")` L33 |
| KEY_OK_DOUBLE_QUOTE | 🔵 OK | `self.ui.get("KEY_OK_DOUBLE_QUOTE", ...)` L34 |
| KEY_OK_DICT_GET | 🟠 GHOST | ten plugin nie łapie `T.get("...")` |
| KEY_OK_SUBDIR | 🟠 GHOST | w submodule/widget.py używany przez `T.get(` |
| KEY_GHOST_COMMENT_ONLY | 🟠 GHOST | w komentarzu |
| KEY_GHOST_STRING_LITERAL | 🟠 GHOST | plain string |
| KEY_GHOST_NEVER_USED | 🟠 GHOST | brak |

---

### Plugin: `underscore_fn` — wzorzec `_("key")` / `gettext("key")`

Regex: `(?:\bgettext\b|\b_)\(\s*["']([^"']+)["']`

Pliki skanowane: `src/utils.py`

| Klucz | Oczekiwany status | Uwaga |
|-------|------------------|-------|
| KEY_OK_UNDERSCORE | 🔵 OK | `_("KEY_OK_UNDERSCORE")` |
| KEY_OK_DOUBLE_QUOTE | 🔵 OK | `gettext.gettext("KEY_OK_DOUBLE_QUOTE")` |
| pozostałe | 🟠 GHOST | nie używają `_()` ani `gettext()` |

> PUŁAPKA: `gettext.gettext(...)` — regex `\bgettext\b` złapie "gettext" w "gettext.gettext",
> ale trzeba sprawdzić czy nie łapie fałszywie `gettext` jako część dłuższej nazwy.

---

### Plugin: `t_fn` — wzorzec `t("key")` / `i18n.t("key")` [JS/React]

Regex: `\bt\(\s*["']([^"']+)["']`

Pliki skanowane: `src/Component.jsx`
Rozszerzenia muszą zawierać `.jsx`

| Klucz | Oczekiwany status | Uwaga |
|-------|------------------|-------|
| KEY_OK_T_FN | 🔵 OK | `t("KEY_OK_T_FN")` |
| KEY_OK_DOUBLE_QUOTE | 🔵 OK | `i18n.t("KEY_OK_DOUBLE_QUOTE")` |
| pozostałe | 🟠 GHOST | |

> PUŁAPKA: regex `\bt\(` może fałszywie złapać `gettext(` — litera `t` przed `(`.
> Sprawdź czy nie ma false positive w plikach .py gdy jednocześnie skaanujesz .py i .jsx.

---

### Plugin: `dollar_t` — wzorzec `{{ $t("key") }}` [Vue]

Regex: `\{\{\s*\$t\(\s*["']([^"']+)["']\s*\)\s*\}\}`

Pliki skanowane: `src/MyView.vue`
Rozszerzenia muszą zawierać `.vue`

| Klucz | Oczekiwany status | Uwaga |
|-------|------------------|-------|
| KEY_OK_DOLLAR_T | 🔵 OK | `{{ $t("KEY_OK_DOLLAR_T") }}` |
| KEY_OK_SINGLE_QUOTE | 🔵 OK | `{{ $t('KEY_OK_SINGLE_QUOTE') }}` |
| KEY_GHOST_COMMENT_ONLY | 🟠 GHOST | jest w komentarzu HTML `<!-- {{ $t(...) }} -->` |
| pozostałe | 🟠 GHOST | |

---

## Przypadki pułapkowe — do weryfikacji ręcznej

### P1: Wieloliniowe wywołanie (KEY_OK_MULTILINE)
```python
text = T.get(
    "KEY_OK_MULTILINE",
    "fallback"
)
```
Obecny regex `T\.get\(\s*["']([^"']+)["']` NIE złapie tego bo `\s*` nie przechodzi przez newline domyślnie.
**Oczekiwanie:** GHOST przy pluginie dict_get (błąd do naprawienia w regex lub w silniku skanowania).

### P2: Komentarz Python (KEY_GHOST_COMMENT_ONLY)
```python
# KEY_GHOST_COMMENT_ONLY pojawia się tutaj tylko jako komentarz
```
Regex `T\.get\(` tego NIE złapie — prawidłowo GHOST.
Ale `key in line` (używane w inspect_and_copy) TO złapie — dlatego kliknięcie klucza może pokazać linię mimo GHOST statusu.
**To jest znany rozdźwięk między SCAN a INSPECT.**

### P3: Plain string (KEY_GHOST_STRING_LITERAL)
```python
plain = "KEY_GHOST_STRING_LITERAL"
```
Regex `T\.get\(` NIE złapie — prawidłowo GHOST.
Ale `key in line` w inspect TO złapie.
**Ten sam rozdźwięk co P2.**

### P4: False positive `_()` w Python
Plik `utils.py` zawiera `_ = gettext.gettext`.
Regex `\b_\(\s*["']` mógłby złapać `_(` z definicji zmiennej — ale ta linia nie zawiera stringa po `_(`, więc powinno być OK.

---

## Jak używać tego zestawu testowego

1. Otwórz UniC
2. Project Settings → Master JSON: wskaż `lang/master.json`
3. Source Code Directory: wskaż `src/`
4. Extensions: `.py,.jsx,.vue` (wszystkie naraz) lub po jednym dla izolowanego testu
5. Load & Initialize Project
6. Załaduj `pl.json` jako cel (żeby DUP był widoczny)
7. Wybierz plugin z dropdown
8. Kliknij SCAN
9. Porównaj kolory z tabelą powyżej

Każde odchylenie od tabeli to bug w UniC lub w definicji pluginu.

---

## Znane ograniczenia regex-based scan (nie są bugami UniC)

| Ograniczenie | Dotyczy | Efekt |
|---|---|---|
| Komentarze Python `# _("klucz")` | `underscore_fn` | Fałszywe OK — klucz w komentarzu jest złapany |
| Komentarze JS `// t("klucz")` | `t_fn` | Fałszywe OK — komentarz JS jest złapany |
| Komentarze HTML `<!-- $t(...) -->` | `dollar_t` | Fałszywe OK — komentarz HTML jest złapany |
| `dict_get` nie łapie `self._t()` | `dict_get` | Klucze używane przez `self._t()` są GHOST — to poprawne! |

Komentarze Python nie dotyczą `dict_get` ani `self_t` bo wzorce te rzadko pojawiają się w komentarzach jako przykłady.
