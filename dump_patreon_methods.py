#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # baseMethods of DVNPatreonContext is at 0xb96e50
    offset = 0xb96e50
    
    flags, count = struct.unpack("<II", data[offset:offset+8])
    print(f"Method List at 0x{offset:x}: Flags=0x{flags:x}, Count={count}")
    
    offset += 8
    for i in range(count):
        m_name_rel = struct.unpack("<i", data[offset:offset+4])[0]
        m_types_rel = struct.unpack("<i", data[offset+4:offset+8])[0]
        m_imp_rel = struct.unpack("<i", data[offset+8:offset+12])[0]
        
        m_name_addr = offset + m_name_rel
        m_imp_addr = (offset + 8 + m_imp_rel) & 0xFFFFFFFF
        
        m_name = data[m_name_addr:].split(b"\x00")[0].decode(errors='ignore')
        print(f"  [{i}] {m_name} -> IMP: 0x{m_imp_addr:x}")
        
        offset += 12

if __name__ == "__main__":
    main()
