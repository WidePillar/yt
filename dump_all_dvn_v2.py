#!/usr/bin/env python3
import struct
import re

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # Find all class names starting with DVN
    class_names = sorted(list(set(re.findall(b'DVN[a-zA-Z0-9_]+', data))))
    
    for name_bytes in class_names:
        name = name_bytes.decode()
        name_off = data.find(name_bytes + b"\x00")
        if name_off == -1: continue
        
        # Search for any 4-byte reference to name_off
        target = name_off
        for i in range(0, len(data) - 4, 1):
            if struct.unpack("<I", data[i:i+4])[0] == target:
                # Potential name field in class_ro_t (+24)
                ro_off = i - 24
                if ro_off < 0: continue
                
                # baseMethods is at +32
                methlist_ptr_full = struct.unpack("<Q", data[ro_off+32:ro_off+40])[0]
                # High bits 0x80... mean fixup. Look for actual pointer.
                # Actually, in this dylib, it seems the pointer is just the lower 32 bits?
                # Or it's the NEXT 8 bytes? No.
                
                # Let's try multiple guesses for methlist_off
                guesses = [
                    methlist_ptr_full & 0xFFFFFF,
                    struct.unpack("<I", data[ro_off+32:ro_off+36])[0],
                    struct.unpack("<I", data[ro_off+40:ro_off+44])[0] # The 0xb9... was at +40?
                ]
                
                for methlist_off in guesses:
                    if 0xb96df0 <= methlist_off < 0xb96df0 + 0x2ff4:
                        print(f"Class {name} at 0x{ro_off:x}, Methlist at 0x{methlist_off:x}")
                        try:
                            flags, count = struct.unpack("<II", data[methlist_off:methlist_off+8])
                            if count > 100: continue # Sanity check
                            curr = methlist_off + 8
                            for _ in range(count):
                                m_name_rel = struct.unpack("<i", data[curr:curr+4])[0]
                                m_imp_rel = struct.unpack("<i", data[curr+8:curr+12])[0]
                                m_name_addr = curr + m_name_rel
                                m_imp_addr = (curr + 8 + m_imp_rel) & 0xFFFFFFFF
                                
                                # Resolve name (it's a selref)
                                try:
                                    selref = struct.unpack("<Q", data[m_name_addr:m_name_addr+8])[0]
                                    str_off = selref & 0xFFFFFF # Mask high bits
                                    m_name = data[str_off:].split(b"\x00")[0].decode(errors='ignore')
                                except: m_name = "<unknown>"
                                
                                print(f"  {m_name} -> IMP: 0x{m_imp_addr:x}")
                                curr += 12
                        except: pass
                        break

if __name__ == "__main__":
    main()
