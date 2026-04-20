#!/usr/bin/env python3
"""Extract YTLite.dylib from .deb and search for DRM-related strings."""
import struct
import tarfile
import io
import os
import re

DEB_FILE = "ytlite_5.2_arm64.deb"

def parse_ar(data):
    """Parse an ar archive and yield (name, content) tuples."""
    if data[:8] != b'!<arch>\n':
        raise ValueError("Not an ar archive")
    pos = 8
    while pos < len(data):
        if pos % 2 == 1:
            pos += 1
        header = data[pos:pos+60]
        if len(header) < 60:
            break
        name = header[0:16].strip().decode('ascii').rstrip('/')
        size = int(header[48:58].strip())
        pos += 60
        content = data[pos:pos+size]
        pos += size
        yield name, content

def main():
    print(f"Reading {DEB_FILE}...")
    with open(DEB_FILE, "rb") as f:
        deb_data = f.read()
    
    print(f"File size: {len(deb_data)} bytes")
    
    dylib_data = None
    
    for name, content in parse_ar(deb_data):
        print(f"  ar member: {name} ({len(content)} bytes)")
        if name.startswith("data.tar"):
            print(f"  Extracting {name}...")
            tar_io = io.BytesIO(content)
            
            # Determine compression
            if name.endswith('.gz'):
                mode = 'r:gz'
            elif name.endswith('.xz'):
                mode = 'r:xz'
            elif name.endswith('.zst') or name.endswith('.zstd'):
                mode = 'r:zst'
            else:
                mode = 'r:*'
            
            try:
                with tarfile.open(fileobj=tar_io, mode=mode) as tar:
                    for member in tar.getmembers():
                        if member.name.endswith('.dylib'):
                            print(f"  Found dylib: {member.name} ({member.size} bytes)")
                            f_extracted = tar.extractfile(member)
                            if f_extracted:
                                dylib_data = f_extracted.read()
                                # Save it
                                out_name = os.path.basename(member.name)
                                with open(out_name, 'wb') as out:
                                    out.write(dylib_data)
                                print(f"  Saved to {out_name}")
            except Exception as e:
                print(f"  Error extracting tar: {e}")
    
    if not dylib_data:
        print("ERROR: No .dylib found in deb!")
        return
    
    print(f"\n{'='*60}")
    print(f"Dylib size: {len(dylib_data)} bytes")
    print(f"{'='*60}")
    
    # Extract all strings (ASCII sequences of 4+ chars)
    strings = re.findall(b'[\x20-\x7e]{4,}', dylib_data)
    
    # Search for DRM-related patterns
    keywords = [
        b'patreon', b'Patreon', b'PATREON',
        b'isPro', b'isPremium', b'isActivated', b'isRegistered',
        b'pro', b'Pro',
        b'FeaturesNotActivated', b'featuresNotActivated',
        b'activated', b'Activated',
        b'premium', b'Premium',
        b'license', b'License',
        b'subscription', b'Subscription',
        b'patron', b'Patron',
        b'validate', b'Validate',
        b'verify', b'Verify',
        b'purchase', b'Purchase',
        b'trial', b'Trial',
        b'expire', b'Expire',
        b'unlock', b'Unlock',
        b'restrict', b'Restrict',
        b'donate', b'Donate',
        b'paid', b'Paid',
        b'free', b'Free',
        b'DRM', b'drm',
    ]
    
    print("\n--- DRM-Related Strings Found ---")
    found = set()
    for s in strings:
        s_str = s.decode('ascii', errors='ignore')
        for kw in keywords:
            if kw in s:
                if s_str not in found:
                    found.add(s_str)
                    # Find offset
                    offset = dylib_data.find(s)
                    print(f"  [0x{offset:08x}] {s_str}")
    
    # Also look for Objective-C method names
    print("\n--- Objective-C Selectors (DRM-related) ---")
    # ObjC selectors are typically stored as plain strings
    objc_patterns = [
        b'isPro', b'setPro', b'isPatron', b'setPatron',
        b'isPremium', b'setPremium', b'isActivated', b'setActivated',
        b'checkLicense', b'validateLicense', b'verifyPurchase',
        b'proEnabled', b'premiumEnabled',
        b'showPaywall', b'showPurchase', b'showPatreon',
        b'featuresEnabled', b'allFeaturesEnabled',
        b'isFullVersion', b'fullVersion',
    ]
    
    for pat in objc_patterns:
        # Search as exact selector or part of a selector
        idx = 0
        while True:
            idx = dylib_data.find(pat, idx)
            if idx == -1:
                break
            # Get surrounding context
            start = max(0, idx - 20)
            end = min(len(dylib_data), idx + len(pat) + 40)
            context = dylib_data[start:end]
            # Clean for display
            context_clean = re.sub(b'[^\x20-\x7e]', b'.', context)
            print(f"  [0x{idx:08x}] {context_clean.decode('ascii')}")
            idx += 1
    
    # Look for class names
    print("\n--- Class Names ---")
    class_pattern = re.compile(b'_OBJC_CLASS_\$_([A-Za-z_][A-Za-z0-9_]*)')
    classes = set()
    for m in class_pattern.finditer(dylib_data):
        cls = m.group(1).decode('ascii')
        classes.add(cls)
    
    # Filter for interesting classes
    interesting = [c for c in sorted(classes) if any(k in c.lower() for k in 
        ['pro', 'premium', 'patron', 'license', 'purchase', 'pay', 'drm', 'activate', 'subscription'])]
    for cls in interesting:
        print(f"  {cls}")
    
    if not interesting:
        print("  (none found matching DRM keywords)")
        print("  All classes:")
        for cls in sorted(classes)[:50]:
            print(f"    {cls}")

if __name__ == "__main__":
    main()
