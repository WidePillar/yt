#import <Foundation/Foundation.h>

%hook DVNPatreonContext
- (BOOL)isPro { return YES; }
- (BOOL)isAuthorized { return YES; }
- (BOOL)proEnabled { return YES; }
- (BOOL)isProUser { return YES; }
- (BOOL)isPremium { return YES; }
- (BOOL)isPremiumUser { return YES; }
- (BOOL)isActivated { return YES; }
%end

%hook YTLHelper
- (BOOL)isPro { return YES; }
- (BOOL)isAuthorized { return YES; }
%end

%hook YTPSettingsBuilder
- (BOOL)isPro { return YES; }
%end

// Force enable ad blocking in case it's disabled by default or by DRM
%hook YTLUserDefaults
- (BOOL)boolForKey:(NSString *)key {
    if ([key isEqualToString:@"noAds"]) return YES;
    return %orig;
}
%end

// Disable the "Support me on Patreon" popups/reminders
%hook YTPromoThrottleController
- (BOOL)canShowThrottledPromo { return NO; }
- (BOOL)canShowThrottledPromoWithFrequencyCap:(id)arg1 { return NO; }
- (BOOL)canShowThrottledPromoWithFrequencyCaps:(id)arg1 { return NO; }
%end
