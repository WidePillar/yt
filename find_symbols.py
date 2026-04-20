#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    offset = 0
    ncmds = struct.unpack("<I", data[16:20])[0]
    offset = 32
    
    symtab_off = 0
    nsyms = 0
    stroff = 0
    strsize = 0
    
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack("<II", data[offset:offset+8])
        if cmd == 0x2: # LC_SYMTAB
            symtab_off, nsyms, stroff, strsize = struct.unpack("<IIII", data[offset+8:offset+24])
            break
        offset += cmdsize

    if symtab_off == 0:
        print("No symtab found")
        return

    print(f"Symtab: {nsyms} symbols, Stroff: 0x{stroff:x}")

    for i in range(nsyms):
        sym_off = symtab_off + i * 16 # nlist_64 is 16 bytes
        str_idx = struct.unpack("<I", data[sym_off:sym_off+4])[0]
        sym_type = data[sym_off+4]
        sym_addr = struct.unpack("<Q", data[sym_off+8:sym_off+16])[0]
        
        if str_idx != 0:
            name = data[stroff + str_idx:].split(b"\x00")[0].decode(errors='ignore')
            if "patreon" in name.lower() or "activated" in name.lower() or "pro" in name.lower():
                print(f"Symbol: {name} -> Addr: 0x{sym_addr:x} (Type: 0x{sym_type:x})")

if __name__ == "__main__":
    main()
