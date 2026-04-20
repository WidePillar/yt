#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    target = 0xf2e52c
    print(f"Searching for relative offsets to 0x{target:x}...")
    for i in range(0, len(data) - 4, 1):
        x = struct.unpack("<i", data[i:i+4])[0]
        if i + x == target:
            print(f"  Found at 0x{i:x}: {x}")
            # Check if it's a method_t
            if i >= 0xb96df0 and i < 0xb96df0 + 0x2ff4:
                imp_rel = struct.unpack("<i", data[i+8:i+12])[0]
                print(f"    Possible IMP: 0x{i + 8 + imp_rel:x}")

if __name__ == "__main__":
    main()
