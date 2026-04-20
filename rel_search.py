#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    targets = [
        ("isPro", 0xf291e2),
        ("DVNPatreonContext", 0xf35855),
    ]

    for name, target_addr in targets:
        print(f"--- Searching for relative offsets to {name} (0x{target_addr:x}) ---")
        # Search every 4 bytes for a signed 32-bit integer x such that
        # i + x == target_addr
        for i in range(0, len(data) - 4, 4):
            x = struct.unpack("<i", data[i:i+4])[0]
            if i + x == target_addr:
                print(f"  Found relative offset at 0x{i:x}: {x}")
                # If we found a method name, the next 8 bytes (two 32-bit ints) should be types and imp
                if name == "isPro":
                    types_off = struct.unpack("<i", data[i+4:i+8])[0]
                    imp_off = struct.unpack("<i", data[i+8:i+12])[0]
                    print(f"    Possible method_t at 0x{i:x}")
                    print(f"    Name:  0x{i + x:x}")
                    print(f"    Types: 0x{i + 4 + types_off:x}")
                    print(f"    IMP:   0x{i + 8 + imp_off:x} (This is the function to patch!)")

if __name__ == "__main__":
    main()
