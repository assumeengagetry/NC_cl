import CoreGraphics
import Foundation
let a=CommandLine.arguments.dropFirst().map{Double($0)!}
let s=CGEventSource(stateID:.hidSystemState)
func event(_ t:CGEventType,_ x:Double,_ y:Double) { CGEvent(mouseEventSource:s,mouseType:t,mouseCursorPosition:CGPoint(x:x,y:y),mouseButton:.left)!.post(tap:.cghidEventTap) }
event(.leftMouseDown,a[0],a[1]);usleep(100000)
if a.count==4 { for i in 1...20 { let f=Double(i)/20;event(.leftMouseDragged,a[0]+f*(a[2]-a[0]),a[1]+f*(a[3]-a[1]));usleep(10000) } }
event(.leftMouseUp,a.count==4 ? a[2]:a[0],a.count==4 ? a[3]:a[1])
