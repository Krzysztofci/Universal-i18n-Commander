import os
import re
import json
import glob

BASE = os.path.join(os.path.dirname(__file__), 'fixtures')
SCRIPTS = os.path.join(os.path.dirname(__file__), 'src')
MASTER = os.path.join(BASE, 'master.json')
TARGET = os.path.join(BASE, 'pl.json')

print('=== Test setup ===')
print('Master:', MASTER)
print('Target:', TARGET)
print('Scripts dir:', SCRIPTS)

with open(MASTER, 'r', encoding='utf-8') as f:
    data_source = json.load(f)
with open(TARGET, 'r', encoding='utf-8') as f:
    data_target = json.load(f)

# Scan usage
usage_map = {k: False for k in data_source.keys() if k != 'lang_name'}
for root_dir, _, files in os.walk(SCRIPTS):
    for file in files:
        if file.endswith('.json'): continue
        path = os.path.join(root_dir, file)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for k in list(usage_map.keys()):
                if usage_map[k]:
                    continue
                pat_quoted = r'["\']' + re.escape(k) + r'["\']'
                if re.search(pat_quoted, content):
                    usage_map[k] = True
                    continue
                pat_word = r'(?<![A-Za-z0-9_])' + re.escape(k) + r'(?![A-Za-z0-9_])'
                if re.search(pat_word, content):
                    usage_map[k] = True

print('\n=== Usage map ===')
for k, v in usage_map.items():
    print(f'{k}:', 'USED' if v else 'UNUSED')

# Duplicate detection in target (translations)
counts = {}
for k, v in data_target.items():
    if not isinstance(v, str):
        continue
    s = v.strip()
    if not s:
        continue
    counts[s.lower()] = counts.get(s.lower(), 0) + 1

print('\n=== Duplicate translations in target ===')
for k, v in data_target.items():
    if not isinstance(v, str):
        continue
    s = v.strip()
    if not s:
        continue
    if counts.get(s.lower(), 0) > 1:
        print(f'KEY {k} has duplicated translation: "{s}"')

# Test add key propagation
new_key = 'added_test'
if new_key in data_source:
    print('\nNew key already exists, removing for test...')
    data_source.pop(new_key, None)
    with open(MASTER, 'w', encoding='utf-8') as f:
        json.dump(data_source, f, indent=4, ensure_ascii=False)

print('\n=== Adding new key to master and propagating ===')
data_source[new_key] = 'New value'
with open(MASTER, 'w', encoding='utf-8') as f:
    json.dump(data_source, f, indent=4, ensure_ascii=False)

for path in glob.glob(os.path.join(BASE, '*.json')):
    if os.path.normpath(path) == os.path.normpath(MASTER):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    if new_key not in d:
        d[new_key] = ''
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(d, f, indent=4, ensure_ascii=False)
    print('Propagated to', path)

# Verify propagation
print('\n=== Verify propagation in target files ===')
for path in glob.glob(os.path.join(BASE, '*.json')):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(os.path.basename(path), 'has', new_key, '->', ('present' if new_key in d else 'missing'))

# Test delete key propagation
print('\n=== Deleting test key from master and targets ===')
if new_key in data_source:
    data_source.pop(new_key, None)
    with open(MASTER, 'w', encoding='utf-8') as f:
        json.dump(data_source, f, indent=4, ensure_ascii=False)

for path in glob.glob(os.path.join(BASE, '*.json')):
    if os.path.normpath(path) == os.path.normpath(MASTER):
        continue
    try:
        with open(path, 'r', encoding='utf-8') as f:
            d = json.load(f)
    except Exception:
        continue
    if new_key in d:
        d.pop(new_key, None)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(d, f, indent=4, ensure_ascii=False)
        print('Removed from', path)

print('\n=== Final check ===')
for path in glob.glob(os.path.join(BASE, '*.json')):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(os.path.basename(path), 'keys:', sorted(list(d.keys())))
