"""
tests/test_plugins.py

Testy regresji pluginów UniC.
Weryfikują że każdy plugin z i18n_plugins.json poprawnie wykrywa klucze
w plikach demo_project/src/ — bez uruchamiania GUI.

Uruchomienie:
    cd Universal-i18n-commander
    pytest tests/test_plugins.py -v
"""

import os
import re
import json
import pytest

# --- Ścieżki ---
ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_FILE = os.path.join(ROOT, "src", "i18n_plugins.json")
DEMO_SRC    = os.path.join(ROOT, "tests", "demo_project", "src")
DEMO_LANG   = os.path.join(ROOT, "tests", "demo_project", "lang")
MASTER_JSON = os.path.join(DEMO_LANG, "master.json")
TARGET_JSON = os.path.join(DEMO_LANG, "pl.json")

# --- Pomocnicza funkcja skanowania (odpowiednik scan_all_keys bez GUI) ---

def scan_with_plugin(plugin: dict, src_dir: str, extensions: list[str]) -> set[str]:
    """Zwraca zbiór kluczy znalezionych przez plugin w plikach src_dir."""
    pattern = plugin["pattern"]
    try:
        rx = re.compile(pattern, re.MULTILINE)
    except re.error as e:
        raise ValueError(f"Plugin '{plugin['id']}' ma niepoprawny regex: {e}")

    found = set()
    for root, _, files in os.walk(src_dir):
        for fname in files:
            if not any(fname.endswith(ext) for ext in extensions):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for match in rx.findall(content):
                key = match.strip() if isinstance(match, str) else match[0].strip()
                if key:
                    found.add(key)
    return found


def detect_duplicates(target_json_path: str) -> set[str]:
    """Zwraca zbiór kluczy których wartość w target JSON jest zduplikowana."""
    with open(target_json_path, encoding="utf-8") as f:
        data = json.load(f)
    counts: dict[str, list[str]] = {}
    for k, v in data.items():
        if not isinstance(v, str) or not v.strip():
            continue
        val = v.strip().lower()
        counts.setdefault(val, []).append(k)
    dups = set()
    for keys in counts.values():
        if len(keys) > 1:
            dups.update(keys)
    return dups


# --- Fixtures pytest ---

@pytest.fixture(scope="session")
def plugins() -> list[dict]:
    with open(PLUGINS_FILE, encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def master_keys() -> set[str]:
    with open(MASTER_JSON, encoding="utf-8") as f:
        data = json.load(f)
    return set(k for k in data if k != "lang_name")

@pytest.fixture(scope="session")
def duplicate_keys() -> set[str]:
    return detect_duplicates(TARGET_JSON)


# ---------------------------------------------------------------------------
# Testy pluginów
# ---------------------------------------------------------------------------

class TestPluginStructure:
    """Weryfikuje że każdy plugin ma wymagane pola i poprawny regex."""

    def test_plugins_file_exists(self):
        assert os.path.isfile(PLUGINS_FILE), f"Brak pliku: {PLUGINS_FILE}"

    def test_plugins_is_nonempty_list(self, plugins):
        assert isinstance(plugins, list)
        assert len(plugins) > 0

    @pytest.mark.parametrize("field", ["id", "name", "pattern", "description"])
    def test_all_plugins_have_required_fields(self, plugins, field):
        for p in plugins:
            assert field in p, f"Plugin '{p.get('id', '?')}' nie ma pola '{field}'"
            assert p[field].strip(), f"Plugin '{p.get('id', '?')}' ma puste pole '{field}'"

    def test_all_plugin_ids_unique(self, plugins):
        ids = [p["id"] for p in plugins]
        assert len(ids) == len(set(ids)), "Zduplikowane ID pluginów"

    def test_all_patterns_compile(self, plugins):
        for p in plugins:
            try:
                re.compile(p["pattern"], re.MULTILINE)
            except re.error as e:
                pytest.fail(f"Plugin '{p['id']}' — błąd regex: {e}")

    def test_all_patterns_have_exactly_one_capture_group(self, plugins):
        for p in plugins:
            rx = re.compile(p["pattern"])
            assert rx.groups == 1, (
                f"Plugin '{p['id']}' ma {rx.groups} grup przechwytujących — wymagana dokładnie 1"
            )


class TestDemoProjectFiles:
    """Weryfikuje że pliki demo_project istnieją."""

    def test_master_json_exists(self):
        assert os.path.isfile(MASTER_JSON)

    def test_target_json_exists(self):
        assert os.path.isfile(TARGET_JSON)

    def test_demo_src_exists(self):
        assert os.path.isdir(DEMO_SRC)

    @pytest.mark.parametrize("fname", [
        "main_app.py", "utils.py", "Component.jsx", "MyView.vue",
        os.path.join("submodule", "widget.py"),
    ])
    def test_demo_src_files_exist(self, fname):
        assert os.path.isfile(os.path.join(DEMO_SRC, fname)), f"Brak pliku demo: {fname}"


class TestDuplicateDetection:
    """Weryfikuje wykrywanie duplikatów w pl.json."""

    def test_dup_keys_detected(self, duplicate_keys):
        assert "KEY_DUP_A" in duplicate_keys
        assert "KEY_DUP_B" in duplicate_keys

    def test_ok_keys_not_duplicated(self, duplicate_keys, master_keys):
        non_dup = master_keys - {"KEY_DUP_A", "KEY_DUP_B"}
        false_dups = non_dup & duplicate_keys
        assert not false_dups, f"Klucze błędnie wykryte jako DUP: {false_dups}"


class TestPluginDictGet:
    """Plugin: T.get() / self.T.get()"""

    PLUGIN_ID = "dict_get"
    EXTENSIONS = [".py"]

    EXPECTED_FOUND = {
        "KEY_OK_DICT_GET",
        "KEY_OK_DOUBLE_QUOTE",
        "KEY_OK_SINGLE_QUOTE",
        "KEY_OK_MULTILINE",
        "KEY_OK_SUBDIR",
        "KEY_DUP_A",
        "KEY_DUP_B",
    }
    EXPECTED_NOT_FOUND = {
        "KEY_GHOST_NEVER_USED",
        "KEY_OK_SELF_T",
        "KEY_OK_UNDERSCORE",
        "KEY_OK_T_FN",
        "KEY_OK_DOLLAR_T",
    }

    @pytest.fixture(scope="class")
    def found(self, plugins):
        p = next((x for x in plugins if x["id"] == self.PLUGIN_ID), None)
        if p is None:
            pytest.skip(f"Plugin '{self.PLUGIN_ID}' nie istnieje w {PLUGINS_FILE}")
        return scan_with_plugin(p, DEMO_SRC, self.EXTENSIONS)

    def test_expected_keys_found(self, found):
        missing = self.EXPECTED_FOUND - found
        assert not missing, f"Plugin '{self.PLUGIN_ID}' nie wykrył kluczy: {missing}"

    def test_ghost_keys_not_found(self, found):
        false_positives = self.EXPECTED_NOT_FOUND & found
        assert not false_positives, f"Plugin '{self.PLUGIN_ID}' błędnie wykrył: {false_positives}"


class TestPluginSelfT:
    """Plugin: self._t() / self.ui.get()"""

    PLUGIN_ID = "self_t"
    EXTENSIONS = [".py"]

    EXPECTED_FOUND = {
        "KEY_OK_SELF_T",
        "KEY_OK_DOUBLE_QUOTE",
    }
    EXPECTED_NOT_FOUND = {
        "KEY_GHOST_NEVER_USED",
        "KEY_OK_DICT_GET",
        "KEY_OK_SUBDIR",
        "KEY_OK_UNDERSCORE",
    }

    @pytest.fixture(scope="class")
    def found(self, plugins):
        p = next((x for x in plugins if x["id"] == self.PLUGIN_ID), None)
        if p is None:
            pytest.skip(f"Plugin '{self.PLUGIN_ID}' nie istnieje")
        return scan_with_plugin(p, DEMO_SRC, self.EXTENSIONS)

    def test_expected_keys_found(self, found):
        missing = self.EXPECTED_FOUND - found
        assert not missing, f"Plugin '{self.PLUGIN_ID}' nie wykrył kluczy: {missing}"

    def test_ghost_keys_not_found(self, found):
        false_positives = self.EXPECTED_NOT_FOUND & found
        assert not false_positives, f"Plugin '{self.PLUGIN_ID}' błędnie wykrył: {false_positives}"


class TestPluginUnderscoreFn:
    """Plugin: _() / gettext()"""

    PLUGIN_ID = "underscore_fn"
    EXTENSIONS = [".py"]

    EXPECTED_FOUND = {
        "KEY_OK_UNDERSCORE",
        # KEY_OK_DOUBLE_QUOTE pominięty — w utils.py używany przez gettext.gettext()
        # co jest celowo wykluczone przez regex (metoda na obiekcie)
    }
    EXPECTED_NOT_FOUND = {
        "KEY_GHOST_NEVER_USED",
        "KEY_OK_DICT_GET",
        "KEY_OK_SELF_T",
        "KEY_OK_DOUBLE_QUOTE",  # gettext.gettext() — nie łapany, poprawne zachowanie
    }

    @pytest.fixture(scope="class")
    def found(self, plugins):
        p = next((x for x in plugins if x["id"] == self.PLUGIN_ID), None)
        if p is None:
            pytest.skip(f"Plugin '{self.PLUGIN_ID}' nie istnieje")
        return scan_with_plugin(p, DEMO_SRC, self.EXTENSIONS)

    def test_expected_keys_found(self, found):
        missing = self.EXPECTED_FOUND - found
        assert not missing, f"Plugin '{self.PLUGIN_ID}' nie wykrył kluczy: {missing}"

    def test_ghost_keys_not_found(self, found):
        false_positives = self.EXPECTED_NOT_FOUND & found
        assert not false_positives, f"Plugin '{self.PLUGIN_ID}' błędnie wykrył: {false_positives}"


class TestPluginTFn:
    """Plugin: t() / i18n.t() [JavaScript]"""

    PLUGIN_ID = "t_fn"
    EXTENSIONS = [".jsx", ".js"]

    EXPECTED_FOUND = {
        "KEY_OK_T_FN",
        "KEY_OK_DOUBLE_QUOTE",
    }
    EXPECTED_NOT_FOUND = {
        "KEY_GHOST_NEVER_USED",
        "KEY_OK_DOLLAR_T",   # $t() nie powinien być złapany przez t_fn
        "KEY_OK_DICT_GET",
    }

    @pytest.fixture(scope="class")
    def found(self, plugins):
        p = next((x for x in plugins if x["id"] == self.PLUGIN_ID), None)
        if p is None:
            pytest.skip(f"Plugin '{self.PLUGIN_ID}' nie istnieje")
        return scan_with_plugin(p, DEMO_SRC, self.EXTENSIONS)

    def test_expected_keys_found(self, found):
        missing = self.EXPECTED_FOUND - found
        assert not missing, f"Plugin '{self.PLUGIN_ID}' nie wykrył kluczy: {missing}"

    def test_dollar_t_not_captured(self, found):
        """Krytyczny test: t_fn NIE może łapać $t() z Vue."""
        assert "KEY_OK_DOLLAR_T" not in found, (
            "Plugin 't_fn' błędnie wykrył KEY_OK_DOLLAR_T — regex łapie $t() z Vue!"
        )


class TestPluginDollarT:
    """Plugin: {{ $t() }} [Vue]"""

    PLUGIN_ID = "dollar_t"
    EXTENSIONS = [".vue"]

    EXPECTED_FOUND = {
        "KEY_OK_DOLLAR_T",
        "KEY_OK_SINGLE_QUOTE",
    }
    EXPECTED_NOT_FOUND = {
        "KEY_GHOST_NEVER_USED",
        "KEY_OK_T_FN",
        "KEY_OK_DICT_GET",
    }

    @pytest.fixture(scope="class")
    def found(self, plugins):
        p = next((x for x in plugins if x["id"] == self.PLUGIN_ID), None)
        if p is None:
            pytest.skip(f"Plugin '{self.PLUGIN_ID}' nie istnieje")
        return scan_with_plugin(p, DEMO_SRC, self.EXTENSIONS)

    def test_expected_keys_found(self, found):
        missing = self.EXPECTED_FOUND - found
        assert not missing, f"Plugin '{self.PLUGIN_ID}' nie wykrył kluczy: {missing}"

    def test_ghost_keys_not_found(self, found):
        false_positives = self.EXPECTED_NOT_FOUND & found
        assert not false_positives, f"Plugin '{self.PLUGIN_ID}' błędnie wykrył: {false_positives}"


class TestPluginPyAll:
    """Plugin: Python all-in-one"""

    PLUGIN_ID = "py_all"
    EXTENSIONS = [".py"]

    # Powinien złapać sumę dict_get + self_t + underscore_fn
    EXPECTED_FOUND = {
        "KEY_OK_DICT_GET",
        "KEY_OK_DOUBLE_QUOTE",
        "KEY_OK_SINGLE_QUOTE",
        "KEY_OK_MULTILINE",
        "KEY_OK_SUBDIR",
        "KEY_OK_SELF_T",
        "KEY_OK_UNDERSCORE",
        "KEY_DUP_A",
        "KEY_DUP_B",
    }
    EXPECTED_NOT_FOUND = {
        "KEY_GHOST_NEVER_USED",
        "KEY_OK_T_FN",
        "KEY_OK_DOLLAR_T",
    }

    @pytest.fixture(scope="class")
    def found(self, plugins):
        p = next((x for x in plugins if x["id"] == self.PLUGIN_ID), None)
        if p is None:
            pytest.skip(f"Plugin '{self.PLUGIN_ID}' nie istnieje — dodaj go do i18n_plugins.json")
        return scan_with_plugin(p, DEMO_SRC, self.EXTENSIONS)

    def test_expected_keys_found(self, found):
        missing = self.EXPECTED_FOUND - found
        assert not missing, f"Plugin '{self.PLUGIN_ID}' nie wykrył kluczy: {missing}"

    def test_js_keys_not_captured(self, found):
        false_positives = self.EXPECTED_NOT_FOUND & found
        assert not false_positives, f"Plugin '{self.PLUGIN_ID}' błędnie wykrył: {false_positives}"
