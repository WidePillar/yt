#!/usr/bin/env python3
import struct
import sys
import re

def read_uleb128(data, offset):
    result = 0
    shift = 0
    while True:
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7f) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return result, offset

def main():
    with open("YTLite.dylib", "rb") as f:
        data = f.read()

    # Find __objc_methname section or just search for strings that look like method names
    # But more importantly, let's look for where the strings like "isPro" or "patreon" are used.
    
    # We found "patreonSection:" at 0x00f28263.
    # Let's see if we can find pointers to this address.
    
    # The address in the file is 0x00f28263.
    # In a Mach-O, we need to know the VM address.
    # Let's find the LC_SEGMENT_64 commands.
    
    offset = 0
    magic = struct.unpack("<I", data[offset:offset+4])[0]
    if magic != 0xfeedfacf:
        print("Not a 64-bit Mach-O")
        return
    
    ncmds = struct.unpack("<I", data[offset+16:offset+20])[0]
    offset = 32
    
    vm_addr_offset = 0
    
    segments = []
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack("<II", data[offset:offset+8])
        if cmd == 0x19: # LC_SEGMENT_64
            segname = data[offset+8:offset+24].strip(b'\x00').decode()
            vmaddr, vmsize, fileoff, filesize = struct.unpack("<QQQQ", data[offset+24:offset+56])
            segments.append({'name': segname, 'vmaddr': vmaddr, 'vmsize': vmsize, 'fileoff': fileoff, 'filesize': filesize})
            if segname == "__TEXT":
                vm_addr_offset = vmaddr
        offset += cmdsize

    print(f"VM Address Offset: 0x{vm_addr_offset:x}")

    def file_to_vm(file_offset):
        for seg in segments:
            if seg['fileoff'] <= file_offset < seg['fileoff'] + seg['filesize']:
                return seg['vmaddr'] + (file_offset - seg['fileoff'])
        return None

    def vm_to_file(vm_addr):
        for seg in segments:
            if seg['vmaddr'] <= vm_addr < seg['vmaddr'] + seg['vmsize']:
                return seg['fileoff'] + (vm_addr - seg['vmaddr'])
        return None

    # Target strings from earlier analysis
    targets = [
        ("patreonSection:", 0x00f28263),
        ("patreonButtonCellWithType:model:", 0x00f2f66a),
        ("DVNPatreonContext", 0x00f35855),
    ]

    for name, file_off in targets:
        vm_addr = file_to_vm(file_off)
        print(f"Target '{name}': File 0x{file_off:x} -> VM 0x{vm_addr:x}")
        
        # Search for pointers to this VM address
        ptr = struct.pack("<Q", vm_addr)
        for i in range(0, len(data) - 8, 8):
            val = struct.unpack("<Q", data[i:i+8])[0]
            if val == vm_addr:
                print(f"  Referenced at File 0x{i:x} (VM 0x{file_to_vm(i):x})")

if __name__ == "__main__":
    main()
