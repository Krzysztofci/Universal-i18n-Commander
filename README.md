# 🌍 Universal i18n Commander (UniC)

**Universal i18n Commander** is a lightweight, portable localization manager designed for JSON-based projects. It streamlines the translation process and helps eliminate "dead" or redundant keys in your codebase.

### 🚀 Why UniC?

- **Portable:** A single script with zero external dependencies (uses Python's standard library).
- **Code-Aware:** Scans your source code in real-time to show which keys are actually in use.
- **JSON-Native UI:** The application's interface is localized via its own JSON files.

### ✨ Key Features

- 🔍 **Smart Scanning:** Automatically detects key usage across your project.
- 🎨 **Status Legend:**
  - 🔵 **Blue (OK):** Key is present in JSON and active in the code.
  - 🟠 **Orange (Ghost Key):** Key exists in JSON but was not found in the source code.
  - 🔴 **Red (Duplicate):** Multiple keys share the same value.
- 📋 **Click-to-Inspect:** Copy keys instantly and see their locations in the code.
- 🔄 **Dynamic UI Language:** Change the interface language on the fly.

### 🛠 Installation & Usage

1. Download the latest version from the **Releases** section (portable) or clone the repo.
2. If running from source:
   ```bash
   python3 src/UniC.py
