import Cocoa
import CoreGraphics
import Foundation
let args=CommandLine.arguments
if args.count>1 && args[1]=="permission" {
 print("screenCaptureAllowed=\(CGPreflightScreenCaptureAccess())")
 exit(0)
}
let all=CGWindowListCopyWindowInfo([.optionOnScreenOnly,.excludeDesktopElements],kCGNullWindowID) as? [[String:Any]] ?? []
for d in all {
 let owner=d[kCGWindowOwnerName as String] as? String ?? ""
 if ["Wireshark","Terminal"].contains(owner), (d[kCGWindowLayer as String] as? Int ?? 1)==0 {
  print(String(data:try! JSONSerialization.data(withJSONObject:d,options:[.sortedKeys]),encoding:.utf8)!)
 }
}
