#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # __objc_classlist: Addr 0x1137f10, Size 0x1d0, Offset 0x1137f10
    start = 0x1137f10
    size = 0x1d0
    
    base = 0x100000000 # Let's try this base again
    
    for i in range(start, start + size, 8):
        ptr_full = struct.unpack("<Q", data[i:i+8])[0]
        ptr = ptr_full - base
        print(f"ClassList at 0x{i:x} -> 0x{ptr_full:x} (Offset: 0x{ptr:x})")
        
        # If we can follow the pointer, let's see if it looks like a class structure
        if 0 <= ptr < len(data) - 40:
            # struct objc_class { isa, super, cache, vtable, data }
            data_ptr_full = struct.unpack("<Q", data[ptr + 32:ptr + 40])[0]
            data_ptr = data_ptr_full - base
            print(f"  data (class_ro_t): 0x{data_ptr_full:x} (Offset: 0x{data_ptr:x})")
            
            if 0 <= data_ptr < len(data) - 32:
                # class_ro_t name pointer is at +24
                name_ptr_full = struct.unpack("<Q", data[data_ptr + 24:data_ptr + 32])[0]
                name_ptr = name_ptr_full - base
                if 0 <= name_ptr < len(data):
                    name = data[name_ptr:].split(b"\x00")[0].decode(errors='ignore')
                    print(f"  Class Name: {name}")

if __name__ == "__main__":
    main()
