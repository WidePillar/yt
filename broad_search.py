#!/usr/bin/env python3
import re
with open("YTLite.dylib", "rb") as f:
    data = f.read()

keywords = [b'isPro', b'isPatron', b'patreon', b'isPremium']
for kw in keywords:
    print(f"--- Search for {kw.decode()} ---")
    for m in re.finditer(kw, data, re.IGNORECASE):
        start = max(0, m.start() - 20)
        end = min(len(data), m.end() + 20)
        context = data[start:end]
        print(f"  [0x{m.start():08x}] {context}")
