#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    target = 0xf28263
    print(f"Searching for relative offsets to 0x{target:x}...")
    
    # Method list range
    start = 0xb96df0
    end = 0xb96df0 + 0x2ff4
    
    for i in range(start, end, 4):
        x = struct.unpack("<i", data[i:i+4])[0]
        if i + x == target:
            print(f"  Found at 0x{i:x}: {x}")
            # Check if it's a method_t
            # method_t { int32_t name; int32_t types; int32_t imp; }
            # It could be the 'name' field.
            types_rel = struct.unpack("<i", data[i+4:i+8])[0]
            imp_rel = struct.unpack("<i", data[i+8:i+12])[0]
            print(f"    Possible IMP: 0x{i + 8 + imp_rel:x}")

if __name__ == "__main__":
    main()
