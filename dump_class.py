#!/usr/bin/env python3
import struct
import sys

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    def get_ptr(off):
        return struct.unpack("<Q", data[off:off+8])[0]

    def get_i32(off):
        return struct.unpack("<i", data[off:off+4])[0]

    # Target class
    target_class_name = "DVNPatreonContext"
    class_name_off = data.find(target_class_name.encode() + b"\x00")
    if class_name_off == -1:
        print(f"Class {target_class_name} not found")
        return
    
    print(f"Class Name '{target_class_name}' at 0x{class_name_off:x}")

    # In Mach-O, __objc_data contains the class structures.
    # A class structure is:
    # struct objc_class {
    #   void *isa;
    #   void *superclass;
    #   void *cache;
    #   void *vtable;
    #   class_rw_t *data; // (points to class_ro_t in binary)
    # }
    
    # Actually, let's search for the pointer to the class name string.
    # This pointer is in the class_ro_t structure.
    # class_ro_t {
    #   uint32_t flags;
    #   uint32_t instanceStart;
    #   uint32_t instanceSize;
    #   uint32_t reserved;
    #   uint8_t *ivarLayout;
    #   char *name; // THIS POINTS TO THE CLASS NAME
    #   ...
    # }

    # Search for pointers to class_name_off
    # (Since it's a dylib, pointers might be absolute VM addresses or relative)
    # Let's assume absolute VM address == file offset for now (common in dylibs at rest)
    
    found_ro = -1
    for i in range(0, len(data) - 8, 8):
        val = get_ptr(i)
        if val == class_name_off:
            # This could be the 'name' field of a class_ro_t
            # name is at offset 24 (3*4 + 8 + 4) if 64-bit... Wait.
            # 64-bit class_ro_t:
            # 0: flags (4)
            # 4: instanceStart (4)
            # 8: instanceSize (4)
            # 12: reserved (4)
            # 16: ivarLayout (8)
            # 24: name (8)  <-- THIS ONE
            # 32: baseMethods (8)
            # 40: baseProtocols (8)
            # 48: ivars (8)
            # ...
            ro_addr = i - 24
            if ro_addr >= 0:
                print(f"Possible class_ro_t at 0x{ro_addr:x}")
                base_methods = get_ptr(ro_addr + 32)
                print(f"  baseMethods: 0x{base_methods:x}")
                if base_methods != 0:
                    # Parse method list
                    # struct method_list_t {
                    #   uint32_t flags;
                    #   uint32_t count;
                    #   struct method_t methods[];
                    # }
                    count = struct.unpack("<I", data[base_methods+4:base_methods+8])[0]
                    print(f"  Method count: {count}")
                    for m in range(count):
                        meth_off = base_methods + 8 + m * 12 # 12 bytes per relative method_t
                        # struct method_t { int32_t name; int32_t types; int32_t imp; }
                        m_name_rel = get_i32(meth_off)
                        m_types_rel = get_i32(meth_off + 4)
                        m_imp_rel = get_i32(meth_off + 8)
                        
                        m_name_addr = meth_off + m_name_rel
                        m_types_addr = meth_off + 4 + m_types_rel
                        m_imp_addr = meth_off + 8 + m_imp_rel
                        
                        m_name = data[m_name_addr:].split(b"\x00")[0].decode(errors='ignore')
                        print(f"    - {m_name} (IMP: 0x{m_imp_addr:x})")

if __name__ == "__main__":
    main()
