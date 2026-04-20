#!/usr/bin/env python3
import struct

def main():
    addr = 0x1286356
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    offset = 0
    ncmds = struct.unpack("<I", data[16:20])[0]
    offset = 32
    
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack("<II", data[offset:offset+8])
        if cmd == 0x19: # LC_SEGMENT_64
            segname = data[offset+8:offset+24].strip(b'\x00').decode()
            vmaddr, vmsize, fileoff, filesize = struct.unpack("<QQQQ", data[offset+24:offset+56])
            if fileoff <= addr < fileoff + filesize:
                print(f"Address 0x{addr:x} is in Segment {segname}")
                nsects = struct.unpack("<I", data[offset+64:offset+68])[0]
                sect_offset = offset + 72
                for _ in range(nsects):
                    sectname = data[sect_offset:sect_offset+16].strip(b'\x00').decode()
                    s_addr, s_size, s_off = struct.unpack("<QQI", data[sect_offset+32:sect_offset+52])
                    if s_off <= addr < s_off + s_size:
                        print(f"  Section {sectname}")
                    sect_offset += 80
        offset += cmdsize

if __name__ == "__main__":
    main()
