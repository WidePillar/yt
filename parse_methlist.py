#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # Section info from previous step
    # __objc_methlist: Offset 0xb96df0, Size 0x2ff4
    methlist_off = 0xb96df0
    methlist_size = 0x2ff4
    
    # __objc_methname: Offset 0xf27860, Size 0xdfe2
    methname_off = 0xf27860
    
    print("--- Parsing __objc_methlist ---")
    
    # Method lists start with a header
    # struct method_list_t {
    #   uint32_t flags;
    #   uint32_t count;
    #   struct method_t methods[];
    # }
    
    # But often there are multiple method lists.
    # Actually, the __objc_const section contains the class structures which point to these lists.
    
    # Let's try searching for the 'isPro' selector in the methlist.
    # 'isPro' is at 0xf291e2.
    target_sel_off = 0xf291e2
    
    # Search for relative offset to target_sel_off in methlist
    for i in range(methlist_off, methlist_off + methlist_size, 4):
        x = struct.unpack("<i", data[i:i+4])[0]
        if i + x == target_sel_off:
            print(f"Found 'isPro' reference in methlist at 0x{i:x}")
            # This is likely a method_t
            # Check if it's the first, second, or third field
            # method_t { int32_t name; int32_t types; int32_t imp; }
            # If i is name:
            types_rel = struct.unpack("<i", data[i+4:i+8])[0]
            imp_rel = struct.unpack("<i", data[i+8:i+12])[0]
            print(f"  Method at 0x{i:x}:")
            print(f"    Name: 0x{i + x:x} ('isPro')")
            print(f"    Types: 0x{i + 4 + types_rel:x}")
            print(f"    IMP: 0x{i + 8 + imp_rel:x}")

if __name__ == "__main__":
    main()
