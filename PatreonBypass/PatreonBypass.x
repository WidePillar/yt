#import <Foundation/Foundation.h>

%hook DVNPatreonContext
- (BOOL)isPro { return YES; }
- (BOOL)isAuthorized { return YES; }
- (BOOL)proEnabled { return YES; }
- (BOOL)isProUser { return YES; }
- (BOOL)isPremium { return YES; }
%end
