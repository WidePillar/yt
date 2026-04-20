#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # Search for ANY 32-bit relative offset to 0xf28263 (patreonSection:)
    target = 0xf28263
    print(f"Searching for relative offsets to 0x{target:x}...")
    for i in range(0, len(data) - 4, 1):
        x = struct.unpack("<i", data[i:i+4])[0]
        if i + x == target:
            print(f"  Found at 0x{i:x}: {x}")

if __name__ == "__main__":
    main()
