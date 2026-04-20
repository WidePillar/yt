#!/usr/bin/env python3
import re
with open("YTLite.dylib", "rb") as f:
    data = f.read()

for m in re.finditer(b'https?://[^\x00\x20\x22\x27]{5,100}', data):
    print(f"URL at 0x{m.start():08x}: {m.group(0).decode('ascii', errors='ignore')}")
