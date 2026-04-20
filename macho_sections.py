#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    offset = 0
    magic = struct.unpack("<I", data[offset:offset+4])[0]
    if magic != 0xfeedfacf:
        print("Not a 64-bit Mach-O")
        return
    
    ncmds = struct.unpack("<I", data[offset+16:offset+20])[0]
    offset = 32
    
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack("<II", data[offset:offset+8])
        if cmd == 0x19: # LC_SEGMENT_64
            segname = data[offset+8:offset+24].strip(b'\x00').decode()
            nsects = struct.unpack("<I", data[offset+64:offset+68])[0]
            print(f"Segment {segname}")
            sect_offset = offset + 72
            for _ in range(nsects):
                sectname = data[sect_offset:sect_offset+16].strip(b'\x00').decode()
                addr, size, f_off = struct.unpack("<QQI", data[sect_offset+32:sect_offset+52])
                print(f"  Section {sectname}: Addr 0x{addr:x}, Size 0x{size:x}, Offset 0x{f_off:x}")
                sect_offset += 80
        offset += cmdsize

if __name__ == "__main__":
    main()
