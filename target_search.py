#!/usr/bin/env python3
"""Targeted extraction of YTLite DRM method addresses."""
import re
import struct

DYLIB = "YTLite.dylib"

def find_all(data, sub):
    start = 0
    while True:
        start = data.find(sub, start)
        if start == -1: return
        yield start
        start += 1

def main():
    with open(DYLIB, "rb") as f:
        data = f.read()
    
    # 1. Search for specific "isPro" / "isPatron" selectors
    targets = [
        b'isPro', b'isProUser', b'isPremium', b'isPremiumUser', 
        b'isPatron', b'isActivated', b'featuresNotActivated',
        b'isFullVersion', b'allFeaturesEnabled'
    ]
    
    print("--- Targeted Selector Search ---")
    for target in targets:
        for addr in find_all(data, target):
            # Check if it's a null-terminated string (likely a selector)
            if data[addr+len(target)] == 0:
                # Look backwards for null or start
                start = addr
                while start > 0 and data[start-1] != 0:
                    start -= 1
                full_str = data[start:addr+len(target)].decode('ascii', errors='ignore')
                print(f"Found selector string: '{full_str}' at 0x{addr:08x}")

    # 2. Search for the classes we saw earlier
    classes = [b'DVNPatreonContext', b'YTLHelper', b'YTPSettingsBuilder']
    print("\n--- Targeted Class Search ---")
    for cls in classes:
        for addr in find_all(data, cls):
            print(f"Found class string: '{cls.decode()}' at 0x{addr:08x}")

    # 3. Look for where these strings are referenced (pointers)
    # On ARM64, pointers are 8 bytes.
    # We look for the address of the string in the data.
    # Note: We need to account for the base address if it's a Mach-O, 
    # but usually we can find the offset in the __objc_selrefs or __objc_classrefs.
    
    # Let's just find the addresses first.

if __name__ == "__main__":
    main()
