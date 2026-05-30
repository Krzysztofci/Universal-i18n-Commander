#!/usr/bin/env python3
"""
TEST FILE: src/main_app.py
Pokrywa wzorce: dict.get("key"), self.T.get("key"), self._t("key"), self.ui.get("key")
"""

# --- Wzorzec dict_get: T.get("klucz", fallback) ---

class AppWindow:
    def __init__(self, translations):
        self.T = translations

    def build_ui(self):
        # OCZEKIWANE OK (plugin: dict_get)
        label_text = T.get("KEY_OK_DICT_GET", "fallback text")
        self.T.get("KEY_OK_DOUBLE_QUOTE", "fallback")

        # OCZEKIWANE OK (plugin: dict_get) — pojedynczy cudzysłów
        T.get('KEY_OK_SINGLE_QUOTE', 'fallback')

        # OCZEKIWANE OK (plugin: dict_get) — wieloliniowe wywołanie
        text = T.get(
            "KEY_OK_MULTILINE",
            "fallback multiline"
        )

        # OCZEKIWANE OK (plugin: dict_get) — duplikaty
        T.get("KEY_DUP_A", "dup a")
        T.get("KEY_DUP_B", "dup b")

        # --- Wzorzec self_t: self._t("klucz"), self.ui.get("klucz") ---

        # OCZEKIWANE OK (plugin: self_t)
        self._t("KEY_OK_SELF_T")
        self.ui.get("KEY_OK_DOUBLE_QUOTE", "fallback")

        # PUŁAPKA: klucz w komentarzu — NIE powinien być zliczany
        # KEY_GHOST_COMMENT_ONLY pojawia się tutaj tylko jako komentarz

        # PUŁAPKA: klucz jako plain string — NIE w wywołaniu tłumaczenia
        plain = "KEY_GHOST_STRING_LITERAL"

        # PUŁAPKA: klucz KEY_GHOST_NEVER_USED — w ogóle nie ma go w tym pliku ani nigdzie

    def _t(self, key, fallback=""):
        return self.T.get(key, fallback)
