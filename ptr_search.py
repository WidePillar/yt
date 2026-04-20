#!/usr/bin/env python3
import struct
import re

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # Find the __TEXT section to get the base VM address
    # Usually dylibs start at VM address 0 in the file but have a base in memory.
    # However, the pointers in the file often use the VM address from the segment commands.

    # Let's find the __objc_methname section if possible, or just the range of the strings.
    # We know strings are around 0xf20000.

    # Let's search for the "isPro" string more carefully.
    is_pro_off = data.find(b"isPro\x00")
    if is_pro_off == -1:
        is_pro_off = data.find(b"isPro")
    
    if is_pro_off != -1:
        print(f"Found 'isPro' at 0x{is_pro_off:x}")
        # Search for any 8-byte aligned pointer to this address
        for i in range(0, len(data) - 8, 8):
            val = struct.unpack("<Q", data[i:i+8])[0]
            if val == is_pro_off:
                print(f"  Pointer to 'isPro' found at 0x{i:x}")
    
    # Let's look for "DVNPatreonContext" class
    patreon_off = data.find(b"DVNPatreonContext\x00")
    if patreon_off != -1:
        print(f"Found 'DVNPatreonContext' at 0x{patreon_off:x}")
        for i in range(0, len(data) - 8, 8):
            val = struct.unpack("<Q", data[i:i+8])[0]
            if val == patreon_off:
                print(f"  Pointer to 'DVNPatreonContext' found at 0x{i:x}")

    # Maybe the pointers are 4-byte? (Unlikely for arm64)
    # Maybe they are relative?
    
    # Let's look for the method list structure.
    # struct objc_method {
    #   uint32_t name; // offset to name string
    #   uint32_t types; // offset to type string
    #   uint32_t imp; // offset to implementation
    # };
    # (In some versions of ObjC runtime, these are relative offsets)

if __name__ == "__main__":
    main()
