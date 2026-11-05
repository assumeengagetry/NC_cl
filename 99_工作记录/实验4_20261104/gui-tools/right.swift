import CoreGraphics
import Foundation
let s=CGEventSource(stateID:.hidSystemState)
let p=CGPoint(x:Double(CommandLine.arguments[1])!,y:Double(CommandLine.arguments[2])!)
CGEvent(mouseEventSource:s,mouseType:.mouseMoved,mouseCursorPosition:p,mouseButton:.right)!.post(tap:.cghidEventTap)
usleep(100000)
CGEvent(mouseEventSource:s,mouseType:.rightMouseDown,mouseCursorPosition:p,mouseButton:.right)!.post(tap:.cghidEventTap)
usleep(100000)
CGEvent(mouseEventSource:s,mouseType:.rightMouseUp,mouseCursorPosition:p,mouseButton:.right)!.post(tap:.cghidEventTap)
