#!/usr/bin/env python3
import sys
import os
import json
import glob
import configparser
import locale
import re

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib

class UniversalI18nManagerGTK(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.universal.i18n.commander")
        self.config_file = "i18n_commander_config.ini"
        self.config = configparser.ConfigParser()
        
        self.data_source = {}
        self.data_target = {}
        self.target_path = ""
        self.active_path = ""
        self.usage_map = {}
        self.entries = {}
        self.sort_mode = "key"
        
        self._load_settings()
        self._init_internal_lang()

    def _load_settings(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        if 'PROJ' not in self.config:
            self.config['PROJ'] = {
                'master_file': '', 'scripts_dir': '', 
                'extensions': '.py,.js,.html', 'ui_lang': 'auto'
            }
        self.master_file = self.config['PROJ'].get('master_file', '')
        self.scripts_dir = self.config['PROJ'].get('scripts_dir', '')
        ext_raw = self.config['PROJ'].get('extensions', '.py,.js,.html')
        self.extensions = [ex.strip() for ex in ext_raw.split(',') if ex.strip()]

    def _init_internal_lang(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.internal_lang_dir = os.path.join(base_dir, "internal_lang")
        if not os.path.exists(self.internal_lang_dir): 
            os.makedirs(self.internal_lang_dir)
            
        self.default_en = {
            "btn_project": "📁 Project Settings", "btn_save": "💾 SAVE", "btn_scan": "🔍 SCAN CODE",
            "lbl_sort": "Sort by:", "lbl_legend": "Legend:",
            "lbl_ok": "■ OK", "lbl_dup": "■ DUP", "lbl_ghost": "■ GHOST",
            "col_key": "SYSTEM KEY", "col_source": "SOURCE (MASTER)", "col_trans": "TRANSLATION",
            "msg_restart": "Restart app to apply changes.", "lbl_ui_lang": "UI Lang:",
            "win_select_title": "Select Target", "btn_load": "Load Selected", "btn_create_new": "Create New",
            "lbl_project_configuration": "⚙️ Project Configuration",
            "lbl_project_setup": "⚙️ Project Setup",
            "lbl_master_json_file": "Master JSON File:",
            "btn_browse_file": "Browse File...",
            "lbl_source_code_directory": "Source Code Directory:",
            "btn_browse_folder": "Browse Folder...",
            "lbl_extensions": "Extensions (comma separated):",
            "btn_apply_project": "🚀 Load & Initialize Project",
            "lbl_target_translations": "📄 Target Translations",
            "btn_new_lang": "➕ New Lang",
            "btn_change_config": "⚙️ Change Config",
            "btn_add_key": "➕ Add Key",
            "btn_del_key": "🗑️ Del Key",
            "lbl_source_header": "🌍 Source: {file}",
            "lbl_source_list_item": "🌍 {file} (source)",
            "lbl_target_list_item": "🌐 {name}",
            "title_language": "Language",
            "title_error": "Error",
            "title_info": "Info",
            "title_ok": "OK",
            "msg_invalid_master_path": "Master JSON file path is invalid or empty!",
            "msg_invalid_master_json": "Invalid Master JSON: {error}",
            "msg_switch_to_source_add": "Switch to the source file before adding a new translation key.",
            "msg_switch_to_source_delete": "Switch to the source file before deleting a key.",
            "msg_key_cannot_be_empty": "Key cannot be empty.",
            "msg_key_already_exists": "This key already exists in the source file.",
            "msg_key_not_found": "Key not found in source file.",
            "msg_saved_successfully": "Saved successfully!",
            "title_add_key": "Add Key to Source",
            "lbl_new_key": "New key:",
            "ph_new_key": "e.g. welcome_message",
            "lbl_source_value": "Source value:",
            "ph_source_value": "e.g. Welcome!",
            "ph_delete_key": "e.g. obsolete_message",
            "btn_create_key": "Create Key",
            "title_delete_key": "Delete Source Key",
            "lbl_key_to_delete": "Key to delete:",
            "btn_delete_key": "Delete Key",
            "title_new_translation": "New Translation",
            "ph_new_translation": "e.g. pl",
            "btn_create": "Create",
            "win_inspect_search": "Search: {key}",
            "win_select_master": "Select MASTER JSON",
            "win_select_source": "Select Source Folder",
            "lbl_editing": "Editing: {name}{source_suffix}",
            "lbl_source_suffix": " (source)"
        }
        
        def _t(key, fallback=None):
            return self.ui.get(key, fallback if fallback is not None else key)
        self._t = _t

        en_path = os.path.join(self.internal_lang_dir, "en.json")
        if not os.path.exists(en_path):
            with open(en_path, 'w', encoding='utf-8') as f: 
                json.dump(self.default_en, f, indent=4)

        self.available_langs = [os.path.splitext(os.path.basename(x))[0] 
                               for x in glob.glob(os.path.join(self.internal_lang_dir, "*.json"))]
        
        saved_lang = self.config['PROJ'].get('ui_lang', 'auto')
        if saved_lang == 'auto' or saved_lang not in self.available_langs:
            try:
                sys_lang = locale.getlocale()[0] or locale.getdefaultlocale()[0]
                self.current_lang_code = 'pl' if sys_lang and sys_lang.startswith('pl') and 'pl' in self.available_langs else 'en'
            except: self.current_lang_code = 'en'
        else: 
            self.current_lang_code = saved_lang

        lang_path = os.path.join(self.internal_lang_dir, f"{self.current_lang_code}.json")
        try:
            with open(lang_path, 'r', encoding='utf-8') as f: 
                self.ui = json.load(f)
        except: 
            self.ui = self.default_en

    def do_activate(self):
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("Universal i18n Commander v4.0 (GTK)")
        self.window.set_default_size(1300, 850)

        # Górny pasek
        header = Gtk.HeaderBar()
        self.window.set_titlebar(header)

        btn_save = Gtk.Button(label=self.ui.get("btn_save", "SAVE"))
        btn_save.add_css_class("suggested-action")  
        btn_save.connect("clicked", self.save_data)
        header.pack_start(btn_save)

        btn_scan = Gtk.Button(label=self.ui.get("btn_scan", "SCAN"))
        btn_scan.connect("clicked", self.scan_all_keys)
        header.pack_start(btn_scan)

        # Język UI
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lang_box.append(Gtk.Label(label=self.ui.get("lbl_ui_lang", "UI:")))
        self.lang_dropdown = Gtk.DropDown.new_from_strings(self.available_langs)
        try:
            idx = self.available_langs.index(self.current_lang_code)
            self.lang_dropdown.set_selected(idx)
        except: pass
        self.lang_dropdown.connect("notify::selected", self.on_ui_lang_change)
        lang_box.append(self.lang_dropdown)
        header.pack_end(lang_box)

        # Główny layout
        main_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.window.set_child(main_layout)

        # --- LEWY PANEL (Używamy Gtk.Stack do przełączania między Formularzem a Listą Języków) ---
        self.sidebar_stack = Gtk.Stack()
        self.sidebar_stack.set_size_request(300, -1)
        self.sidebar_stack.set_margin_top(10)
        self.sidebar_stack.set_margin_bottom(10)
        self.sidebar_stack.set_margin_start(10)
        self.sidebar_stack.set_margin_end(10)

        # 1. WIDOK FORMULARZA (Gdy projekt nie jest ustawiony)
        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        lbl_setup = Gtk.Label(label=self.ui.get("lbl_project_configuration", "⚙️ Project Configuration"), xalign=0)
        lbl_setup.set_markup(f'<span weight="bold" size="large">{self.ui.get("lbl_project_setup", "⚙️ Project Setup")}</span>')
        form_box.append(lbl_setup)

        form_box.append(Gtk.Label(label=self.ui.get("lbl_master_json_file", "Master JSON File:"), xalign=0))
        self.ent_master_path = Gtk.Entry(text=self.master_file)
        form_box.append(self.ent_master_path)
        btn_browse_master = Gtk.Button(label=self.ui.get("btn_browse_file", "Browse File..."))
        btn_browse_master.connect("clicked", self.on_browse_master)
        form_box.append(btn_browse_master)

        form_box.append(Gtk.Label(label=self.ui.get("lbl_source_code_directory", "Source Code Directory:"), xalign=0))
        self.ent_src_path = Gtk.Entry(text=self.scripts_dir)
        form_box.append(self.ent_src_path)
        btn_browse_src = Gtk.Button(label=self.ui.get("btn_browse_folder", "Browse Folder..."))
        btn_browse_src.connect("clicked", self.on_browse_src)
        form_box.append(btn_browse_src)

        form_box.append(Gtk.Label(label=self.ui.get("lbl_extensions", "Extensions (comma separated):"), xalign=0))
        self.ent_extensions = Gtk.Entry(text=",".join(self.extensions))
        form_box.append(self.ent_extensions)

        btn_apply_project = Gtk.Button(label=self.ui.get("btn_apply_project", "🚀 Load & Initialize Project"))
        btn_apply_project.add_css_class("suggested-action")
        btn_apply_project.connect("clicked", self.on_apply_project_form)
        form_box.append(btn_apply_project)

        self.sidebar_stack.add_named(form_box, "form")

        # 2. WIDOK LISTY (Gdy projekt jest poprawnie wczytany)
        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        lbl_sidebar = Gtk.Label(label=self.ui.get("lbl_target_translations", "📄 Target Translations"), xalign=0)
        lbl_sidebar.set_markup(f'<span weight="bold">{self.ui.get("lbl_target_translations", "📄 Target Translations")}</span>')
        list_box.append(lbl_sidebar)

        self.source_version_label = Gtk.Label(label="", xalign=0)
        self.source_version_label.set_wrap(True)
        self.source_version_label.set_margin_bottom(10)
        list_box.append(self.source_version_label)

        self.sidebar_listbox = Gtk.ListBox()
        self.sidebar_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_listbox.connect("row-selected", self.on_target_selected)
        
        scroll_sidebar = Gtk.ScrolledWindow()
        scroll_sidebar.set_vexpand(True)
        scroll_sidebar.set_child(self.sidebar_listbox)
        list_box.append(scroll_sidebar)

        action_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        btn_new_target = Gtk.Button(label=self.ui.get("btn_new_lang", "➕ New Lang"))
        btn_new_target.connect("clicked", lambda b: self._create_new_target())
        action_buttons.append(btn_new_target)

        btn_edit_config = Gtk.Button(label=self.ui.get("btn_change_config", "⚙️ Change Config"))
        btn_edit_config.connect("clicked", lambda b: self.sidebar_stack.set_visible_child_name("form"))
        action_buttons.append(btn_edit_config)
        list_box.append(action_buttons)

        self.sidebar_stack.add_named(list_box, "list")

        main_layout.append(self.sidebar_stack)
        main_layout.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))

        # Prawy panel
        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        right_panel.set_hexpand(True)
        right_panel.set_vexpand(True)
        right_panel.set_margin_top(15)
        right_panel.set_margin_bottom(15)
        right_panel.set_margin_start(15)
        right_panel.set_margin_end(15)
        main_layout.append(right_panel)

        filter_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        right_panel.append(filter_bar)

        sort_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        sort_box.append(Gtk.Label(label=self.ui.get("lbl_sort", "Sort:")))
        self.sort_dropdown = Gtk.DropDown.new_from_strings(["Key", "Source", "Target"])
        self.sort_dropdown.connect("notify::selected", self.on_sort_change)
        sort_box.append(self.sort_dropdown)
        filter_bar.append(sort_box)

        btn_add_key = Gtk.Button(label=self.ui.get("btn_add_key", "➕ Add Key"))
        btn_add_key.connect("clicked", self.on_add_key)
        filter_bar.append(btn_add_key)

        btn_del_key = Gtk.Button(label=self.ui.get("btn_del_key", "🗑️ Del Key"))
        btn_del_key.connect("clicked", self.on_del_key)
        filter_bar.append(btn_del_key)

        legend_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        legend_box.append(Gtk.Label(label=self.ui.get("lbl_legend", "Legend:")))
        
        lbl_ok = Gtk.Label(); lbl_ok.set_markup(f'<span foreground="#2980b9" weight="bold">{self.ui.get("lbl_ok", "■ OK")}</span>')
        lbl_dup = Gtk.Label(); lbl_dup.set_markup(f'<span foreground="#e74c3c" weight="bold">{self.ui.get("lbl_dup", "■ DUP")}</span>')
        lbl_ghost = Gtk.Label(); lbl_ghost.set_markup(f'<span foreground="#e67e22" weight="bold">{self.ui.get("lbl_ghost", "■ GHOST")}</span>')
        
        legend_box.append(lbl_ok)
        legend_box.append(lbl_dup)
        legend_box.append(lbl_ghost)
        filter_bar.append(legend_box)

        self.status_label = Gtk.Label(label=self.ui.get("lbl_status_idle", "..."), xalign=1)
        self.status_label.set_hexpand(True)
        filter_bar.append(self.status_label)

        self.scroll_content = Gtk.ScrolledWindow()
        self.scroll_content.set_vexpand(True)
        right_panel.append(self.scroll_content)

        self.window.present()

        # Decyzja co wyświetlić na start
        if self.master_file and os.path.exists(self.master_file):
            self.load_project(auto=True)
        else:
            self.sidebar_stack.set_visible_child_name("form")

    def on_ui_lang_change(self, dropdown, pspec):
        selected_text = self.available_langs[dropdown.get_selected()]
        self.config['PROJ']['ui_lang'] = selected_text
        with open(self.config_file, 'w') as f: self.config.write(f)
        self.show_message(self.ui.get("title_language", "Language"), self.ui.get("msg_restart", "Restart app to apply!"))

    def on_sort_change(self, dropdown, pspec):
        mapping = ["key", "source", "target"]
        self.sort_mode = mapping[dropdown.get_selected()]
        self._fill_data()

    # Obsługa przeglądania plików bezpośrednio z formularza bocznego
    def on_browse_master(self, btn):
        dialog = Gtk.FileDialog(title=self.ui.get("win_select_master", "Select MASTER JSON"))
        file_filter = Gtk.FileFilter()
        file_filter.set_name("JSON files")
        file_filter.add_suffix("json")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(file_filter)
        dialog.set_filters(filters)
        dialog.open(self.window, None, self._on_master_chosen)

    def _on_master_chosen(self, dialog, result):
        try:
            gfile = dialog.open_finish(result)
            self.ent_master_path.set_text(gfile.get_path())
        except: pass

    def on_browse_src(self, btn):
        dialog = Gtk.FileDialog(title=self.ui.get("win_select_source", "Select Source Folder"))
        dialog.select_folder(self.window, None, self._on_src_chosen)

    def _on_src_chosen(self, dialog, result):
        try:
            gfile = dialog.select_folder_finish(result)
            self.ent_src_path.set_text(gfile.get_path())
        except: pass

    # Uruchomienie projektu po kliknięciu przycisku w formularzu
    def on_apply_project_form(self, btn):
        m_file = self.ent_master_path.get_text().strip()
        s_dir = self.ent_src_path.get_text().strip()
        exts = self.ent_extensions.get_text().strip()

        if not m_file or not os.path.exists(m_file):
            self.show_message(self.ui.get("title_error", "Error"), self.ui.get("msg_invalid_master_path", "Master JSON file path is invalid or empty!"))
            return

        self.config['PROJ'].update({'master_file': m_file, 'scripts_dir': s_dir, 'extensions': exts})
        with open(self.config_file, 'w') as f: self.config.write(f)

        self.data_source = {}; self.data_target = {}; self.target_path = ""; self.usage_map = {}
        self._load_settings()
        self.load_project()

    def load_project(self, auto=False):
        if not os.path.exists(self.master_file):
            self.sidebar_stack.set_visible_child_name("form")
            return
            
        self.lang_dir = os.path.dirname(self.master_file)
        try:
            with open(self.master_file, 'r', encoding='utf-8') as f: 
                self.data_source = json.load(f)
        except Exception as e:
            self.show_message(self.ui.get("title_error", "Error"), self.ui.get("msg_invalid_master_json", "Invalid Master JSON: {error}").format(error=e))
            self.sidebar_stack.set_visible_child_name("form")
            return
        
        targets = [os.path.basename(x) for x in glob.glob(os.path.join(self.lang_dir, "*.json")) 
                   if os.path.normpath(x) != os.path.normpath(self.master_file)]
        
        while self.sidebar_listbox.get_first_child():
            self.sidebar_listbox.remove(self.sidebar_listbox.get_first_child())

        self.source_version_label.set_markup(
            f'<span foreground="#2980b9" weight="bold">{self.ui.get("lbl_source_header", "🌍 Source: {file}").format(file=os.path.basename(self.master_file))}</span>'
        )

        source_row = Gtk.ListBoxRow()
        source_lbl = Gtk.Label(label=self.ui.get("lbl_source_list_item", "🌍 {file} (source)").format(file=os.path.basename(self.master_file)), xalign=0)
        source_lbl.set_margin_top(5)
        source_lbl.set_margin_bottom(5)
        source_lbl.set_margin_start(5)
        source_lbl.set_margin_end(5)
        source_row.set_child(source_lbl)
        source_row.file_path = self.master_file
        source_row.is_source = True
        self.sidebar_listbox.append(source_row)

        for t in targets:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label(label=self.ui.get("lbl_target_list_item", "🌐 {name}").format(name=t), xalign=0)
            lbl.set_margin_top(5)
            lbl.set_margin_bottom(5)
            lbl.set_margin_start(5)
            lbl.set_margin_end(5)
            row.set_child(lbl)
            row.file_path = os.path.join(self.lang_dir, t)
            row.is_source = False
            self.sidebar_listbox.append(row)

        # Przełącz widok na listę języków
        self.sidebar_stack.set_visible_child_name("list")

        if not targets:
            self._create_new_target()
        elif auto and len(targets) == 1:
            self.target_path = os.path.join(self.lang_dir, targets[0])
            self.active_path = self.target_path
            self._load_target_and_fill()

    def on_target_selected(self, listbox, row):
        if row is None: return
        self.target_path = row.file_path
        self.active_path = row.file_path
        self._load_target_and_fill()

    def on_add_key(self, btn):
        if self.active_path != self.master_file:
            self.show_message(self.ui.get("title_info", "Info"), self.ui.get("msg_switch_to_source_add", "Switch to the source file before adding a new translation key."))
            return

        win = Gtk.Window(title=self.ui.get("title_add_key", "Add Key to Source"))
        win.set_default_size(360, 180)
        win.set_transient_for(self.window)
        win.set_modal(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(12); box.set_margin_bottom(12); box.set_margin_start(12); box.set_margin_end(12)

        box.append(Gtk.Label(label=self.ui.get("lbl_new_key", "New key:")))
        key_entry = Gtk.Entry()
        key_entry.set_placeholder_text(self.ui.get("ph_new_key", "e.g. welcome_message"))
        box.append(key_entry)

        box.append(Gtk.Label(label=self.ui.get("lbl_source_value", "Source value:")))
        value_entry = Gtk.Entry()
        value_entry.set_placeholder_text(self.ui.get("ph_source_value", "e.g. Welcome!"))
        box.append(value_entry)

        btn_create = Gtk.Button(label=self.ui.get("btn_create_key", "Create Key"))
        def on_create_clicked(button):
            new_key = key_entry.get_text().strip()
            source_value = value_entry.get_text().strip()
            if not new_key:
                self.show_message(self.ui.get("title_error", "Error"), self.ui.get("msg_key_cannot_be_empty", "Key cannot be empty."))
                return
            if new_key in self.data_source:
                self.show_message(self.ui.get("title_error", "Error"), self.ui.get("msg_key_already_exists", "This key already exists in the source file."))
                return

            self.data_source[new_key] = source_value
            self.data_target[new_key] = ""
            self._save_json(self.master_file, self.data_source)
            self._propagate_new_key_to_targets(new_key)
            self._fill_data()
            win.destroy()
        btn_create.connect("clicked", on_create_clicked)
        box.append(btn_create)

        win.set_child(box)
        win.present()

    def on_del_key(self, btn):
        if self.active_path != self.master_file:
            self.show_message(self.ui.get("title_info", "Info"), self.ui.get("msg_switch_to_source_delete", "Switch to the source file before deleting a key."))
            return

        win = Gtk.Window(title=self.ui.get("title_delete_key", "Delete Source Key"))
        win.set_default_size(360, 140)
        win.set_transient_for(self.window)
        win.set_modal(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(12); box.set_margin_bottom(12); box.set_margin_start(12); box.set_margin_end(12)

        box.append(Gtk.Label(label=self.ui.get("lbl_key_to_delete", "Key to delete:")))
        key_entry = Gtk.Entry()
        key_entry.set_placeholder_text(self.ui.get("ph_delete_key", "e.g. obsolete_message"))
        box.append(key_entry)

        btn_delete = Gtk.Button(label=self.ui.get("btn_delete_key", "Delete Key"))
        def on_delete_clicked(button):
            key_to_delete = key_entry.get_text().strip()
            if not key_to_delete:
                self.show_message(self.ui.get("title_error", "Error"), self.ui.get("msg_key_cannot_be_empty", "Key cannot be empty."))
                self.show_message(self.ui.get("title_error", "Error"), self.ui.get("msg_key_not_found", "Key not found in source file."))
                return

            self.data_source.pop(key_to_delete, None)
            self._save_json(self.master_file, self.data_source)
            self._delete_key_from_targets(key_to_delete)
            if key_to_delete in self.data_target:
                self.data_target.pop(key_to_delete, None)
            self._fill_data()
            win.destroy()
        btn_delete.connect("clicked", on_delete_clicked)
        box.append(btn_delete)

        win.set_child(box)
        win.present()

    def _delete_key_from_targets(self, key):
        if not self.lang_dir or not os.path.isdir(self.lang_dir):
            return
        for path in glob.glob(os.path.join(self.lang_dir, "*.json")):
            if os.path.normpath(path) == os.path.normpath(self.master_file):
                continue
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    target_data = json.load(f)
            except Exception:
                continue
            if key in target_data:
                target_data.pop(key, None)
                self._save_json(path, target_data)

    def _create_new_target(self):
        win_input = Gtk.Window(title=self.ui.get("title_new_translation", "New Translation"))
        win_input.set_default_size(300, 100)
        win_input.set_transient_for(self.window)
        win_input.set_modal(True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10); box.set_margin_bottom(10); box.set_margin_start(10); box.set_margin_end(10)
        entry = Gtk.Entry(placeholder_text=self.ui.get("ph_new_translation", "e.g. pl"))
        btn = Gtk.Button(label=self.ui.get("btn_create", "Create"))
        
        def on_create_click(b):
            new_name = entry.get_text().strip()
            if new_name:
                if not new_name.endswith(".json"): new_name += ".json"
                self.target_path = os.path.join(self.lang_dir, new_name)
                self.data_target = {k: "" for k in self.data_source.keys()}
                if "lang_name" in self.data_source: self.data_target["lang_name"] = new_name.split('.')[0]
                with open(self.target_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data_target, f, indent=4, ensure_ascii=False)
                win_input.destroy()
                self.load_project()
            
        btn.connect("clicked", on_create_click)
        box.append(entry)
        box.append(btn)
        win_input.set_child(box)
        win_input.present()

    def _load_target_and_fill(self):
        if os.path.exists(self.target_path):
            with open(self.target_path, 'r', encoding='utf-8') as f: 
                self.data_target = json.load(f)
        self._fill_data()

    def scan_all_keys(self, btn):
        if not self.scripts_dir: return
        self.usage_map = {k: False for k in self.data_source.keys() if k != "lang_name"}
        for root_dir, _, files in os.walk(self.scripts_dir):
            for file in files:
                if file.endswith(".json") or not any(file.endswith(ex) for ex in self.extensions):
                    continue
                try:
                    with open(os.path.join(root_dir, file), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for k in list(self.usage_map.keys()):
                            if self.usage_map.get(k):
                                continue
                            # Prefer quoted matches ("key" or 'key') to avoid false positives.
                            pat_quoted = r'["\']' + re.escape(k) + r'["\']'
                            if re.search(pat_quoted, content):
                                self.usage_map[k] = True
                                continue
                            # Fallback: match with non-word boundaries around key to reduce substring hits.
                            pat_word = r'(?<![A-Za-z0-9_])' + re.escape(k) + r'(?![A-Za-z0-9_])'
                            if re.search(pat_word, content):
                                self.usage_map[k] = True
                except:
                    continue
        self._fill_data()

    def _fill_data(self):
        self.scroll_content.set_child(None)
        if not self.data_source: return
        
        active_name = os.path.basename(self.target_path) if self.target_path else 'None'
        self.status_label.set_text(
            self.ui.get(
                "lbl_editing",
                "Editing: {name}{source_suffix}"
            ).format(
                name=active_name,
                source_suffix=self.ui.get("lbl_source_suffix", " (source)") if self.target_path == self.master_file else ""
            )
        )
        
        items = [{"key": k, "source": str(v), "target": str(self.data_target.get(k, ""))} 
                 for k, v in self.data_source.items() if k != "lang_name"]
        
        m = self.sort_mode
        items.sort(key=lambda x: x[m].lower())
        
        # Count duplicate translation values in the current target (skip empty translations)
        counts = {}
        for item in items:
            t = item["target"].strip()
            if t:
                tl = t.lower()
                counts[tl] = counts.get(tl, 0) + 1

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(12)
        grid.set_margin_top(10); grid.set_margin_bottom(10); grid.set_margin_start(10); grid.set_margin_end(10)

        h1 = Gtk.Label(label=self.ui.get("col_key", "KEY")); h1.add_css_class("bold")
        h2 = Gtk.Label(label=self.ui.get("col_source", "SOURCE")); h2.add_css_class("bold")
        trans_label = self.ui.get("col_trans", "TRANSLATION")
        if self.target_path == self.master_file:
            trans_label = self.ui.get("col_source", "SOURCE")
        h3 = Gtk.Label(label=trans_label); h3.add_css_class("bold")
        
        grid.attach(h1, 0, 0, 1, 1)
        grid.attach(h2, 1, 0, 1, 1)
        grid.attach(h3, 2, 0, 1, 1)

        self.entries = {}
        for i, item in enumerate(items, start=1):
            key = item["key"]
            # Determine duplicate by checking repeated translation values in current target
            is_dup = False
            target_val = item["target"].strip()
            if target_val and counts.get(target_val.lower(), 0) > 1:
                is_dup = True

            color = "#2980b9"
            if self.usage_map and not self.usage_map.get(key, False):
                color = "#e67e22"
            if is_dup:
                color = "#e74c3c"

            btn_key = Gtk.Button()
            lbl_btn = Gtk.Label()
            lbl_btn.set_markup(f'<span foreground="{color}" weight="bold">{key}</span>')
            btn_key.set_child(lbl_btn)
            btn_key.set_has_frame(False)
            btn_key.connect("clicked", lambda b, k=key: self.inspect_and_copy(k))
            
            lbl_src = Gtk.Label(label=item["source"], xalign=0)
            lbl_src.set_wrap(True)
            lbl_src.set_max_width_chars(45)

            ent_trans = Gtk.Entry()
            ent_trans.set_text(item["target"])
            ent_trans.set_hexpand(True)
            self.entries[key] = ent_trans

            grid.attach(btn_key, 0, i, 1, 1)
            grid.attach(lbl_src, 1, i, 1, 1)
            grid.attach(ent_trans, 2, i, 1, 1)

        self.scroll_content.set_child(grid)

    def inspect_and_copy(self, key):
        clipboard = self.window.get_clipboard()
        clipboard.set(key)
        
        found = []
        if self.scripts_dir:
            for root_dir, _, files in os.walk(self.scripts_dir):
                for file in files:
                    if any(file.endswith(ex) for ex in self.extensions):
                        try:
                            with open(os.path.join(root_dir, file), 'r', encoding='utf-8', errors='ignore') as f:
                                for i, line in enumerate(f, 1):
                                    if key in line: 
                                        found.append(f"{file} (Line {i}): {line.strip()}")
                        except: continue
                        
        win_inspect = Gtk.Window(title=self.ui.get("win_inspect_search", "Search: {key}").format(key=key))
        win_inspect.set_default_size(600, 400)
        win_inspect.set_transient_for(self.window)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_margin_top(10); scroll.set_margin_bottom(10); scroll.set_margin_start(10); scroll.set_margin_end(10)
        
        text_view = Gtk.TextView()
        text_view.set_editable(False)
        buffer = text_view.get_buffer()
        buffer.set_text("\n".join(found))
        
        scroll.set_child(text_view)
        win_inspect.set_child(scroll)
        win_inspect.present()

    def save_data(self, btn):
        if not self.target_path: return
        out = {k: e.get_text() for k, e in self.entries.items()}
        if "lang_name" in self.data_target: 
            out["lang_name"] = self.data_target["lang_name"]
        self._save_json(self.target_path, out)
        if self.target_path == self.master_file:
            self.data_source = out
        self.data_target = out
        self.show_message(self.ui.get("title_ok", "OK"), self.ui.get("msg_saved_successfully", "Saved successfully!"))

    def _save_json(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _propagate_new_key_to_targets(self, key):
        if not self.lang_dir or not os.path.isdir(self.lang_dir):
            return
        for path in glob.glob(os.path.join(self.lang_dir, "*.json")):
            if os.path.normpath(path) == os.path.normpath(self.master_file):
                continue
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    target_data = json.load(f)
            except Exception:
                continue
            if key not in target_data:
                target_data[key] = ""
                self._save_json(path, target_data)

    def show_message(self, title, msg):
        alert = Gtk.AlertDialog(message=msg)
        alert.set_detail(title)
        alert.show(self.window)

if __name__ == "__main__":
    app = UniversalI18nManagerGTK()
    sys.exit(app.run(sys.argv))
