#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    start = 0x11468c0
    size = 0x4198
    methname_start = 0xf27860
    methname_end = methname_start + 0xdfe2
    
    for i in range(start, start + size, 8):
        ptr = struct.unpack("<Q", data[i:i+8])[0]
        # In this binary, it seems high bits are used for PAC/fixups
        # Let's try just the lower 24 or 32 bits
        off = ptr & 0xFFFFFF
        if methname_start <= off < methname_end:
            try:
                name = data[off:].split(b"\x00")[0].decode(errors='ignore')
                if name:
                    interesting = ["patreon", "pro", "premium", "authorized", "activated"]
                    if any(k in name.lower() for k in interesting):
                        print(f"SelRef 0x{i:x}: 0x{ptr:x} -> {name}")
            except: pass

if __name__ == "__main__":
    main()
