#!/usr/bin/env python3
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), '..')
PAGES_DIR = os.path.join(ROOT, 'garden', 'pages')

def backfill():
    updated = 0
    for dirpath, dirnames, filenames in os.walk(PAGES_DIR):
        for fn in filenames:
            if fn.lower() != 'content.md':
                continue
            fp = os.path.join(dirpath, fn)
            with open(fp, 'r', encoding='utf-8') as f:
                text = f.read()

            m = re.search(r'^(---\n)(.*?)(\n---)', text, re.DOTALL | re.MULTILINE)
            if not m:
                continue
            fm = m.group(2)
            if re.search(r'^display_size\s*:', fm, re.MULTILINE):
                continue

            # insert display_size before the closing --- of frontmatter
            new_fm = fm.rstrip() + '\ndisplay_size: square\n'
            new_text = text[:m.start(2)] + new_fm + text[m.end(2):]
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(new_text)
            updated += 1

    print(f"Backfilled {updated} files with display_size: square")

if __name__ == '__main__':
    backfill()
