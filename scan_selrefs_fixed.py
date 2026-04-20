#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # __objc_selrefs: Addr 0x11468c0, Size 0x4198, Offset 0x11468c0
    start = 0x11468c0
    size = 0x4198
    
    # Based on the hex dump, pointers are absolute with a base of 0x100000000
    base = 0x100000000
    
    for i in range(start, start + size, 8):
        ptr_full = struct.unpack("<Q", data[i:i+8])[0]
        ptr = ptr_full - base
        if 0 <= ptr < len(data):
            try:
                name = data[ptr:].split(b"\x00")[0].decode(errors='ignore')
                # Filter for interesting ones
                interesting = ["patreon", "pro", "premium", "authorized", "activated"]
                if any(k in name.lower() for k in interesting):
                    print(f"SelRef at 0x{i:x} -> 0x{ptr_full:x} ('{name}')")
            except: pass

if __name__ == "__main__":
    main()
