# Client Code

from SharedLibs import *
import errno
import sys
from threading import Timer
import curses
from curses.textpad import Textbox, rectangle

ReciveStatus = {"R_Succesfull": 0, "R_NoValidConnection": 1, "R_NothingOccurred": 2, "R_GenericError": 3}
SendStatus = {"S_GettingInput":0, "S_GotInput":1}

HEADER_LENGTH = 10

IP = "192.168.43.140"
PORT = 2359
my_username = input("Username: ")
isMine = 0

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
        print("done")

client_socket = Socket(IPVersion.IPv4)
client_socket.Creat()
client_socket.Connect(IP, PORT)
client_socket.SetBlocking(False)
client_socket.Send(my_username)

inputs = [client_socket]
outputs = [client_socket]

def sendUI(stdscr):
    h = curses.LINES
    w = curses.COLS
    stdscr.addstr(h - 2, 0, my_username)
    winHieght = 1
    winWidth = w - len(my_username) - 3
    winyBegin = h - 2
    winxBegin = len(my_username) + 1

    inputWin = curses.newwin(winHieght, winWidth, winyBegin, winxBegin)
    box = Textbox(inputWin)
    rectangle(stdscr, winyBegin - 1, winxBegin - 1, h -1, w - 2)    
    stdscr.refresh()
    
    box.edit()
    message = box.gather()

    if message:
        client_socket.Send(message)

def main(stdscr):
    stdscr.nodelay(True)
    timer = RepeatTimer(1, sendUI, args=[stdscr])
    timer.start()

    NINPUTS = 0
    pad = curses.newpad(100, 100)
    stdscr.refresh()

    height = curses.LINES
    width = curses.COLS
    padStartLine = 0

    while True:
        try:
            while True:
                buffer = client_socket.Receive()

                if buffer == SockResult.R_GenericError:
                    continue

                flag, username, message = buffer.split(' ', 2)

                isMine = int(flag)

                if isMine == 1:
                    senderName = "You"
                else:
                    senderName = username
                pad.addstr(NINPUTS, 0, senderName + '> ' + message)
                NINPUTS += 1
                if NINPUTS >=  height - 3:
                    padStartLine += 1
                pad.refresh(padStartLine,0, 0,0, height - 4,width - 2)
                stdscr.refresh()

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                # stdscr.clear()
                stdscr.addstr('Reading error: {}'.format(str(e)))
                stdscr.refresh()
                sys.exit()()
            # didn't receive anything
            continue

        except Exception as e:
            stdscr.clear()
            stdscr.addstr('Reading error: {}'.format(str(e)))
            stdscr.refresh()
            sys.exit()()

curses.wrapper(main)