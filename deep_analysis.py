#!/usr/bin/env python3
"""Deep analysis of YTLite.dylib for Patreon DRM bypass."""
import re
import struct

DYLIB = "YTLite.dylib"

def main():
    with open(DYLIB, "rb") as f:
        data = f.read()
    
    print(f"Dylib size: {len(data)} bytes\n")
    
    # 1. Search for YTLite-specific strings (not ffmpeg noise)
    print("=" * 60)
    print("1. YTLite-Specific Strings")
    print("=" * 60)
    
    ytlite_keywords = [
        b'YTLite', b'ytlite', b'YTLITE',
        b'Patreon', b'patreon',
        b'patron', b'Patron',
        b'premium', b'Premium',
        b'activate', b'Activate',
        b'purchase', b'Purchase', 
        b'subscribe', b'Subscribe',
        b'unlock', b'Unlock',
        b'trial', b'Trial',
        b'expire', b'Expire',
        b'license', b'License',
        b'validate', b'Validate',
        b'receipt', b'Receipt',
        b'restore', b'Restore',
        b'paywall', b'Paywall',
        b'features_not', b'FeaturesNot',
        b'isPro', b'is_pro', b'kPro',
        b'proUser', b'ProUser',
        b'fullVersion', b'FullVersion',
        b'dvntm',  # developer bundle id prefix
        b'dayanch',
        b'com.dvntm',
        b'NSUserDefaults',
        b'kYTLite', b'YTLitePro', b'ytlitePro',
        b'isEnabled', b'setEnabled',
        b'featureEnabled', b'FeatureEnabled',
        b'proFeature', b'ProFeature',
        b'Settings', b'settings',
        b'toggle', b'Toggle',
        b'enabled', b'disabled',
        b'adBlock', b'AdBlock', b'adblock',
        b'noAds', b'NoAds',
        b'sponsor', b'Sponsor',
        b'background', b'Background',
        b'download', b'Download',
        b'pip', b'PiP', b'pictureInPicture',
    ]
    
    found_strs = {}
    for kw in ytlite_keywords:
        idx = 0
        while True:
            idx = data.find(kw, idx)
            if idx == -1:
                break
            # Get surrounding context
            start = max(0, idx - 30)
            end = min(len(data), idx + len(kw) + 50)
            context = data[start:end]
            context_clean = re.sub(b'[^\x20-\x7e]', b'.', context).decode('ascii')
            key = f"[0x{idx:08x}] {context_clean}"
            if key not in found_strs:
                found_strs[key] = True
                # Skip ffmpeg noise
                if any(noise in context_clean for noise in ['ffmpeg', 'ffprobe', 'libav', '_ff_', 'avcodec', 'avformat', 'swscale', 'swresample']):
                    idx += 1
                    continue
                print(f"  {key}")
            idx += 1
    
    # 2. Look for NSUserDefaults keys (common DRM storage)
    print("\n" + "=" * 60)
    print("2. NSUserDefaults / Preferences Keys")
    print("=" * 60)
    
    # Find strings that look like preference keys
    pref_patterns = [
        b'kYT', b'YTLite_', b'ytlite_', b'com.dvntm',
        b'isProUser', b'isPremiumUser', b'proEnabled',
        b'kEnabled', b'_enabled', b'_disabled',
        b'featureFlag', b'FeatureFlag',
    ]
    for pat in pref_patterns:
        idx = 0
        while True:
            idx = data.find(pat, idx)
            if idx == -1:
                break
            start = max(0, idx - 10)
            end = min(len(data), idx + 60)
            context = data[start:end]
            context_clean = re.sub(b'[^\x20-\x7e]', b'.', context).decode('ascii')
            print(f"  [0x{idx:08x}] {context_clean}")
            idx += 1
    
    # 3. Mach-O analysis - find ObjC methods
    print("\n" + "=" * 60)
    print("3. All Objective-C Selectors (non-Apple, non-ffmpeg)")
    print("=" * 60)
    
    # Find __objc_methnames section
    # Search for common ObjC method patterns
    selectors = set()
    # Look for null-terminated ASCII strings that look like selectors
    for m in re.finditer(b'((?:[a-zA-Z_][a-zA-Z0-9_]*:?){1,10})\x00', data):
        sel = m.group(1).decode('ascii', errors='ignore')
        # Filter: skip very short, skip Apple/ffmpeg
        if len(sel) < 5:
            continue
        if any(skip in sel.lower() for skip in ['ffmpeg', 'ffprobe', 'avcodec', 'avformat', '_ff_']):
            continue
        # Only keep selectors with colons (methods) or camelCase (properties)
        if ':' in sel or (sel[0].islower() and any(c.isupper() for c in sel[1:])):
            # Filter for interesting ones
            interesting_words = ['pro', 'premium', 'patron', 'license', 'purchase', 
                               'activate', 'enable', 'disable', 'feature', 'unlock',
                               'setting', 'toggle', 'ytlite', 'block', 'ads', 'ad',
                               'subscribe', 'payment', 'restore', 'verify', 'check',
                               'validate', 'receipt', 'store', 'buy', 'paid', 'free',
                               'trial', 'expire', 'limit', 'restrict', 'access',
                               'background', 'download', 'pip', 'sponsor', 'quality',
                               'speed', 'shorts', 'tab', 'hide', 'remove', 'skip']
            if any(w in sel.lower() for w in interesting_words):
                offset = m.start()
                selectors.add((offset, sel))
    
    for offset, sel in sorted(selectors):
        print(f"  [0x{offset:08x}] {sel}")
    
    # 4. Look for URL patterns
    print("\n" + "=" * 60)
    print("4. URLs found")
    print("=" * 60)
    
    for m in re.finditer(b'https?://[^\x00\x20\x22\x27]{5,200}', data):
        url = m.group(0).decode('ascii', errors='ignore')
        if any(skip in url for skip in ['ffmpeg', 'apple.com/DTD', 'schemas.', 'xmlsoap', 'w3.org', 'purl.org']):
            continue
        print(f"  [0x{m.start():08x}] {url}")

if __name__ == "__main__":
    main()
