#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # __objc_selrefs: Addr 0x11468c0, Size 0x4198, Offset 0x11468c0
    start = 0x11468c0
    size = 0x4198
    
    for i in range(start, start + size, 8):
        ptr = struct.unpack("<Q", data[i:i+8])[0]
        if 0xf27860 <= ptr < 0xf27860 + 0xdfe2:
            try:
                name = data[ptr:].split(b"\x00")[0].decode(errors='ignore')
                print(f"SelRef at 0x{i:x} -> 0x{ptr:x} ('{name}')")
            except: pass

if __name__ == "__main__":
    main()
