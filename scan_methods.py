#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    methlist_off = 0xb96df0
    methlist_size = 0x2ff4
    
    offset = methlist_off
    while offset < methlist_off + methlist_size:
        flags, count = struct.unpack("<II", data[offset:offset+8])
        # Flags 0x8000000c is common for relative methods
        if flags & 0x80000000:
            offset += 8
            for _ in range(count):
                m_name_rel = struct.unpack("<i", data[offset:offset+4])[0]
                m_types_rel = struct.unpack("<i", data[offset+4:offset+8])[0]
                m_imp_rel = struct.unpack("<i", data[offset+8:offset+12])[0]
                
                m_name_addr = offset + m_name_rel
                m_imp_addr = (offset + 8 + m_imp_rel) & 0xFFFFFFFF
                
                try:
                    m_name = data[m_name_addr:].split(b"\x00")[0].decode(errors='ignore')
                except:
                    m_name = "<invalid>"
                
                if m_name:
                    # Filter for interesting ones
                    interesting = ["pro", "patron", "authorized", "activated", "premium", "license", "is"]
                    if any(i in m_name.lower() for i in interesting):
                        print(f"Method: {m_name} at Offset 0x{offset:x} -> IMP: 0x{m_imp_addr:x}")
                
                offset += 12
        else:
            # Skip or handle non-relative (absolute) method list
            offset += 4 # Just move a bit

if __name__ == "__main__":
    main()
