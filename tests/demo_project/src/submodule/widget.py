#!/usr/bin/env python3
"""
TEST FILE: src/submodule/widget.py
Testuje czy UniC skanuje PODKATALOGI rekurencyjnie.
Klucz KEY_OK_SUBDIR jest TYLKO tutaj — jeśli UniC go nie znajdzie,
znaczy że nie schodzi do podkatalogów.
"""

class SubWidget:
    def __init__(self, T):
        self.T = T

    def label(self):
        # OCZEKIWANE OK (plugin: dict_get) — tylko w podkatalogu
        return T.get("KEY_OK_SUBDIR", "fallback")
