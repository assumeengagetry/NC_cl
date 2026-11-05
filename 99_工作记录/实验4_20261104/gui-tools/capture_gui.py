from pathlib import Path
import subprocess,time
W=Path(__file__).resolve().parent.parent
SHOT=W/'evidence/screenshots'
MOUSE=W/'gui-tools/mouse'
def osa(s):
 return subprocess.check_output(['osascript','-e',s],text=True)
def menu(name,group='View'):
 osa(f'tell application "System Events" to tell process "Wireshark" to click menu item "{name}" of menu "{group}" of menu bar item "{group}" of menu bar 1')
 time.sleep(.2)
def click(x,y):
 subprocess.run([str(MOUSE),str(x),str(y)],check=True);time.sleep(.15)
def open_cap(name):
 subprocess.run(['open','-a','Wireshark',str(W/'evidence'/name)],check=True);time.sleep(.6)
def frame(n):
 osa('tell application "Wireshark" to activate');time.sleep(.2)
 menu('Go to Packet…','Go')
 osa(f'tell application "System Events" to tell process "Wireshark"\nkeystroke "{n}"\nkey code 36\nend tell');time.sleep(.3)
def capture(name):
 subprocess.run(['screencapture','-x','-o','-l','7182',str(SHOT/(name+'.png'))],check=True)
def compact_echo():
 menu('Collapse All');click(92,142);click(92,124)
if __name__=='__main__':
 open_cap('05-ping-ttl03.pcapng');compact_echo();capture('05-ttl3-request')
 frame(2);capture('06-ttl3-error-check')
