#!/usr/bin/env python3
import struct

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # Find pointers to "YTLHelper" class name (0xf35d84)
    target = 0xf35d84
    # Search for pointer value 0x1000000000 + 0xf35d84
    ptr_val = 0x1000000000 + target
    ptr_bytes = struct.pack("<Q", ptr_val)
    
    found_ro = -1
    for i in range(0, len(data) - 8, 8):
        if data[i:i+8] == ptr_bytes:
            # Check if it's name field of class_ro_t (at +24)
            ro_off = i - 24
            print(f"Found class_ro_t for YTLHelper at 0x{ro_off:x}")
            base_methods_ptr = struct.unpack("<Q", data[ro_off+32:ro_off+40])[0]
            # This is likely a chained fixup. Let's look at the raw bytes.
            print(f"  baseMethods raw: {data[ro_off+32:ro_off+40].hex()}")
            
            # Usually baseMethods points to an offset in __objc_methlist
            # Let's search for any reference to a methlist address
            # Or just look for the methlist structure near the pointers we see.

if __name__ == "__main__":
    main()
