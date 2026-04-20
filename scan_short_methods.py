#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    methlist_off = 0xb96df0
    methlist_size = 0x2ff4
    
    offset = methlist_off
    while offset < methlist_off + methlist_size:
        try:
            flags, count = struct.unpack("<II", data[offset:offset+8])
        except: break
        
        if flags & 0x80000000:
            offset += 8
            for _ in range(count):
                m_name_rel = struct.unpack("<i", data[offset:offset+4])[0]
                m_imp_rel = struct.unpack("<i", data[offset+8:offset+12])[0]
                
                m_name_addr = offset + m_name_rel
                m_imp_addr = (offset + 8 + m_imp_rel) & 0xFFFFFFFF
                
                try:
                    # In this binary, name_rel points to a selref (8 bytes)
                    ptr = struct.unpack("<Q", data[m_name_addr:m_name_addr+8])[0]
                    # String is at ptr - 0x1000000000
                    str_off = ptr - 0x1000000000
                    m_name = data[str_off:].split(b"\x00")[0].decode(errors='ignore')
                except:
                    m_name = "<invalid>"
                
                if len(m_name) == 1:
                    print(f"Short Method: {m_name} (IMP: 0x{m_imp_addr:x})")
                
                offset += 12
        else:
            offset += 4

if __name__ == "__main__":
    main()
