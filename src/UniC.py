#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import glob
import configparser
import locale

class UniversalI18nManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal i18n Commander v3.0")
        self.root.geometry("1300x900")
        
        self.config_file = "i18n_commander_config.ini"
        self.config = configparser.ConfigParser()
        
        self.data_source = {}
        self.data_target = {}
        self.target_path = ""
        self.usage_map = {}
        self.entries = {}
        
        self._load_settings()
        self._init_internal_lang()
        self._setup_ui()
        
        if self.master_file and os.path.exists(self.master_file):
            self.load_project(auto=True)

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
            "btn_project": "📁 PROJECT", "btn_save": "💾 SAVE", "btn_scan": "🔍 SCAN CODE",
            "lbl_sort": " Sort by ", "lbl_legend": " Status Legend ",
            "lbl_ok": "■ OK", "lbl_dup": "■ DUP (Red)", "lbl_ghost": "■ GHOST (Orange)",
            "col_key": "SYSTEM KEY", "col_source": "SOURCE (MASTER)", "col_trans": "TRANSLATION",
            "msg_restart": "Restart app to apply changes.", "lbl_ui_lang": "UI Lang:",
            "win_select_title": "Select Target", "btn_load": "Load Selected", "btn_create_new": "Create New"
        }
        
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

    def _setup_ui(self):
        for widget in self.root.winfo_children(): widget.destroy()
        top = ttk.Frame(self.root, padding="10"); top.pack(fill=tk.X)
        
        ttk.Button(top, text=self.ui.get("btn_project", "PROJECT"), command=self.setup_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text=self.ui.get("btn_save", "SAVE"), command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text=self.ui.get("btn_scan", "SCAN"), command=self.scan_all_keys).pack(side=tk.LEFT, padx=5)
        
        lang_frame = ttk.Frame(top); lang_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(lang_frame, text=self.ui.get("lbl_ui_lang", "UI:")).pack(side=tk.LEFT, padx=2)
        self.lang_combo = ttk.Combobox(lang_frame, values=self.available_langs, width=5, state="readonly")
        self.lang_combo.set(self.current_lang_code)
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_ui_lang_change)
        self.lang_combo.pack(side=tk.LEFT)

        self.sort_mode = tk.StringVar(value="key")
        sort_frame = ttk.LabelFrame(top, text=self.ui.get("lbl_sort", "Sort"), padding="5"); sort_frame.pack(side=tk.LEFT, padx=10)
        for text, val in [("Key", "key"), ("Source", "source"), ("Target", "target")]:
            ttk.Radiobutton(sort_frame, text=text, variable=self.sort_mode, value=val, command=self._fill_data).pack(side=tk.LEFT, padx=5)

        leg = ttk.LabelFrame(top, text=self.ui.get("lbl_legend", "Legend"), padding="5"); leg.pack(side=tk.LEFT, padx=20)
        tk.Label(leg, text=self.ui.get("lbl_ok", "OK"), fg="#2980b9", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(leg, text=self.ui.get("lbl_dup", "DUP"), fg="#e74c3c", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(leg, text=self.ui.get("lbl_ghost", "GHOST"), fg="#e67e22", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(top, text="...", font=('Arial', 9, 'italic')); self.status_label.pack(side=tk.RIGHT, padx=10)

        self.container = ttk.Frame(self.root); self.container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas = tk.Canvas(self.container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scroll_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.scroll_window, width=e.width))
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.configure(yscrollcommand=self.scrollbar.set); self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def on_ui_lang_change(self, event):
        self.config['PROJ']['ui_lang'] = self.lang_combo.get()
        with open(self.config_file, 'w') as f: self.config.write(f)
        messagebox.showinfo("Language", self.ui.get("msg_restart", "Restart app!"))

    def setup_project(self):
        m_file = filedialog.askopenfilename(title="Select MASTER JSON", filetypes=[("JSON files", "*.json")])
        if not m_file: return
        s_dir = filedialog.askdirectory(title="Select folder with source code")
        if not s_dir: return
        exts = simpledialog.askstring("Extensions", "Enter extensions (comma separated):", initialvalue=",".join(self.extensions))
        self.config['PROJ'].update({'master_file': m_file, 'scripts_dir': s_dir, 'extensions': exts or ".py"})
        with open(self.config_file, 'w') as f: self.config.write(f)
        self.data_source = {}; self.data_target = {}; self.target_path = ""; self.usage_map = {}
        self._load_settings(); self.load_project()

    def load_project(self, auto=False):
        if not os.path.exists(self.master_file): return
        self.lang_dir = os.path.dirname(self.master_file)
        try:
            with open(self.master_file, 'r', encoding='utf-8') as f: self.data_source = json.load(f)
        except Exception as e: messagebox.showerror("Error", f"Invalid Master JSON: {e}"); return
        
        targets = [os.path.basename(x) for x in glob.glob(os.path.join(self.lang_dir, "*.json")) 
                   if os.path.normpath(x) != os.path.normpath(self.master_file)]
        
        if not targets:
            self._create_new_target()
        elif auto and len(targets) == 1:
            self.target_path = os.path.join(self.lang_dir, targets[0]); self._load_target_and_fill()
        else:
            self._ask_target_ui(targets)

    def _create_new_target(self, popup_parent=None):
        new_name = simpledialog.askstring("New File", "Enter language code (e.g. 'pl'):", parent=popup_parent or self.root)
        if not new_name: return
        if not new_name.endswith(".json"): new_name += ".json"
        self.target_path = os.path.join(self.lang_dir, new_name)
        self.data_target = {k: "" for k in self.data_source.keys()}
        if "lang_name" in self.data_source: self.data_target["lang_name"] = new_name.split('.')[0]
        with open(self.target_path, 'w', encoding='utf-8') as f:
            json.dump(self.data_target, f, indent=4, ensure_ascii=False)
        self._fill_data()

    def _ask_target_ui(self, targets):
        win = tk.Toplevel(self.root)
        win.title(self.ui.get("win_select_title", "Select Target Language"))
        win.geometry("450x350")
        
        lb = tk.Listbox(win, width=50); lb.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        for t in targets: lb.insert(tk.END, t)
        
        btn_frame = ttk.Frame(win); btn_frame.pack(fill=tk.X, pady=10)
        
        def select():
            if lb.curselection():
                self.target_path = os.path.join(self.lang_dir, lb.get(lb.curselection()))
                self._load_target_and_fill(); win.destroy()
        
        def create_new():
            self._create_new_target(popup_parent=win); win.destroy()

        ttk.Button(btn_frame, text=self.ui.get("btn_load", "Load Selected"), command=select).pack(side=tk.LEFT, padx=20, expand=True)
        ttk.Button(btn_frame, text=self.ui.get("btn_create_new", "Create New"), command=create_new).pack(side=tk.LEFT, padx=20, expand=True)

    def _load_target_and_fill(self):
        if os.path.exists(self.target_path):
            with open(self.target_path, 'r', encoding='utf-8') as f: self.data_target = json.load(f)
        self._fill_data()

    def scan_all_keys(self):
        if not self.scripts_dir: return
        self.usage_map = {k: False for k in self.data_source.keys() if k != "lang_name"}
        for root_dir, _, files in os.walk(self.scripts_dir):
            for file in files:
                if file.endswith(".json") or not any(file.endswith(ex) for ex in self.extensions): continue
                try:
                    with open(os.path.join(root_dir, file), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for k in self.usage_map:
                            if not self.usage_map[k] and k in content: self.usage_map[k] = True
                except: continue
        self._fill_data()

    def _fill_data(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        if not self.data_source: return
        self.status_label.config(text=f"Editing: {os.path.basename(self.target_path) if self.target_path else 'None'}")
        
        items = [{"key": k, "source": str(v), "target": str(self.data_target.get(k, ""))} 
                 for k, v in self.data_source.items() if k != "lang_name"]
        m = self.sort_mode.get(); items.sort(key=lambda x: x[m].lower())
        counts = {}
        for item in items: s = item["source"].strip().lower(); counts[s] = counts.get(s, 0) + 1

        self.scrollable_frame.columnconfigure(2, weight=1); self.entries = {}
        ttk.Label(self.scrollable_frame, text=self.ui.get("col_key", "KEY"), font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(self.scrollable_frame, text=self.ui.get("col_source", "SOURCE"), font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(self.scrollable_frame, text=self.ui.get("col_trans", "TRANS"), font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=10, pady=5)

        for i, item in enumerate(items, start=1):
            key = item["key"]; is_dup = counts[item["source"].strip().lower()] > 1
            color = "#2980b9"
            if self.usage_map and not self.usage_map.get(key, False): color = "#e67e22"
            if is_dup: color = "#e74c3c"
            btn = tk.Button(self.scrollable_frame, text=key, fg=color, relief="flat", font=("Arial", 9, "bold"), command=lambda k=key: self.inspect_and_copy(k))
            btn.grid(row=i, column=0, sticky="w", padx=10, pady=2)
            ttk.Label(self.scrollable_frame, text=item["source"], font=("Arial", 9), wraplength=400).grid(row=i, column=1, sticky="w", padx=10)
            ent = ttk.Entry(self.scrollable_frame, font=("Arial", 10), width=60); ent.insert(0, item["target"]); ent.grid(row=i, column=2, padx=10, pady=2, sticky="we"); self.entries[key] = ent

    def inspect_and_copy(self, key):
        self.root.clipboard_clear(); self.root.clipboard_append(key); found = []
        if self.scripts_dir:
            for root_dir, _, files in os.walk(self.scripts_dir):
                for file in files:
                    if any(file.endswith(ex) for ex in self.extensions):
                        try:
                            with open(os.path.join(root_dir, file), 'r', encoding='utf-8', errors='ignore') as f:
                                for i, line in enumerate(f, 1):
                                    if key in line: found.append(f"{file} (L{i}): {line.strip()}")
                        except: continue
        win = tk.Toplevel(self.root); win.title(f"Search: {key}"); txt = tk.Text(win, padx=10, pady=10)
        txt.pack(fill=tk.BOTH, expand=True)
        for f in found: txt.insert(tk.END, f + "\n")
        txt.config(state="disabled")

    def save_data(self):
        if not self.target_path: return
        out = {k: e.get() for k, e in self.entries.items()}
        if "lang_name" in self.data_target: out["lang_name"] = self.data_target["lang_name"]
        with open(self.target_path, 'w', encoding='utf-8') as f: json.dump(out, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("OK", "Saved!")

if __name__ == "__main__":
    root = tk.Tk(); app = UniversalI18nManager(root); root.mainloop()
