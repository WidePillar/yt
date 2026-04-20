#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # Find all class names starting with DVN
    import re
    class_names = re.findall(b'DVN[a-zA-Z0-9_]+', data)
    class_names = sorted(list(set(class_names)))
    
    for name_bytes in class_names:
        name = name_bytes.decode()
        name_off = data.find(name_bytes + b"\x00")
        if name_off == -1: continue
        
        # Search for pointers to name_off (absolute 0x1000000000 base)
        target = 0x1000000000 + name_off
        ptr_bytes = struct.pack("<Q", target)
        
        for i in range(0, len(data) - 8, 8):
            if data[i:i+8] == ptr_bytes:
                ro_off = i - 24
                if ro_off < 0: continue
                # flags, instStart, instSize, reserved, layout, name, methods, ...
                try:
                    methlist_ptr = struct.unpack("<Q", data[ro_off+32:ro_off+40])[0]
                    # Chained fixup or relative?
                    # Let's assume it's like YTLite (0xb96e50)
                    # Actually, let's look for the 0xb96000 range
                    if (methlist_ptr & 0xFFF000) == 0xb96000:
                        methlist_off = methlist_ptr & 0xFFFFFF
                        print(f"Class {name} at 0x{ro_off:x}, Methlist at 0x{methlist_off:x}")
                        # Dump methods
                        flags, count = struct.unpack("<II", data[methlist_off:methlist_off+8])
                        curr = methlist_off + 8
                        for _ in range(count):
                            m_name_rel = struct.unpack("<i", data[curr:curr+4])[0]
                            m_imp_rel = struct.unpack("<i", data[curr+8:curr+12])[0]
                            
                            m_name_addr = curr + m_name_rel
                            m_imp_addr = (curr + 8 + m_imp_rel) & 0xFFFFFFFF
                            
                            # Resolve name (it's a selref)
                            try:
                                selref = struct.unpack("<Q", data[m_name_addr:m_name_addr+8])[0]
                                str_off = selref - 0x1000000000
                                m_name = data[str_off:].split(b"\x00")[0].decode(errors='ignore')
                            except: m_name = "<invalid>"
                            
                            print(f"  {m_name} -> IMP: 0x{m_imp_addr:x}")
                            curr += 12
                except: pass

if __name__ == "__main__":
    main()
