#!/usr/bin/env python3
"""
TEST FILE: src/utils.py
Pokrywa wzorzec: _("klucz"), gettext("klucz")
"""
import gettext

_ = gettext.gettext

def render_labels():
    # OCZEKIWANE OK (plugin: underscore_fn)
    label = _("KEY_OK_UNDERSCORE")

    # OCZEKIWANE OK (plugin: underscore_fn) — przez gettext wprost
    title = gettext.gettext("KEY_OK_DOUBLE_QUOTE")

    # PUŁAPKA: samo wywołanie bez tłumaczenia
    raw = "KEY_GHOST_STRING_LITERAL"

    # PUŁAPKA: w komentarzu
    # _("KEY_GHOST_COMMENT_ONLY") — to jest wykomentowane

    return label, title
