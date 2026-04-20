#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    target = 0xf28263
    methlist_start = 0xb96df0
    methlist_end = 0xb96df0 + 0x2ff4
    
    print(f"Searching for offsets relative to methlist_start (0x{methlist_start:x})...")
    for i in range(methlist_start, methlist_end, 4):
        x = struct.unpack("<i", data[i:i+4])[0]
        if methlist_start + x == target:
            print(f"  Found at 0x{i:x}: x=0x{x:x}")

    print(f"Searching for offsets relative to current position (i)...")
    for i in range(methlist_start, methlist_end, 4):
        x = struct.unpack("<i", data[i:i+4])[0]
        if i + x == target:
            print(f"  Found at 0x{i:x}: x=0x{x:x}")

    # What if it's absolute but only 32-bit?
    print(f"Searching for absolute 32-bit offsets...")
    for i in range(methlist_start, methlist_end, 4):
        x = struct.unpack("<I", data[i:i+4])[0]
        if x == target:
            print(f"  Found absolute 32-bit at 0x{i:x}")

if __name__ == "__main__":
    main()
