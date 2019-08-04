#!/usr/bin/env python3

import curses as C 
import math
import pyglet
import random as R
import time
import sys
import termios
import tty
import os

playMap = ["WWWWWWWWWWWWWW",
           "W            W",
           "W            W",
           "W  .    WW   W",
           "W            W",
           "W            W",
           "WWWWWWWWWWWWWW"]

WALL = "RGW"

#WALL_h = 50

inputKeys =  {'w':'forward', 
              's':'backward',
              'a':'left',
              'd':'right',
              'P':'exit'}

cNum = 1

pieceSize = 50
playerPos = {}
playerDir = 0

#moveSpeed
PMS = 8
#rotationSpeed
PRS = 5
#viewDistance
PVD = 400
#fieldOfView
FOV = 80#VARIABLE - columns
#rayCastFidelity
RCF = 50


def displaying(_pos,_dir):
    rayOutput = []

    #for every FOV point send out a ray
    #+1 - fine number of rays (symetry)
    for loop in range(FOV+1):
        testDir = _dir - int(FOV/2) + loop

        #submodules of ray
        #works as number guessing game (lower/higher)
        #separate ray into many with different lengths 
        #to higher fidelity of view determination
        #PVD part
        _PVDP = PVD/RCF
        collided = False
        for testLength in range(1,RCF+1):
            #test PVD
            _PVD = testLength*_PVDP
            forwardX = math.sin(math.radians(testDir))
            forwardY = math.cos(math.radians(testDir))

            #rayX = int(_PVD*forwardX)
            #rayY = int(_PVD*forwardY)

            #print(testDir-_dir)
            N = int(_PVD/math.cos(math.radians(testDir-_dir)))

            rayX = int(N*math.sin(math.radians(testDir)))
            rayY = int(N*math.cos(math.radians(testDir)))

            #print(rayX,rayY)
            #continue

            collision = rayCast(rayX,rayY,_pos)

            if(collision != ' '):
                collided = True
                rayOutput.append([collision, _PVD])
                break

        if not (collided):
            rayOutput.append([' ', PVD])
            
    return rayOutput

def rayCast(_rayX,_rayY,_pos):
    #Test ray XY coordinates
    
    rayX = _rayX
    rayY = _rayY

    #scan map for all pieces
    for y in range(len(playMap)):
        _y = list(playMap[y])

        for x in range(len(_y)):
            if(_y[x] != ' ' and _y[x] != '.'):
                xPos = x
                yPos = y

                #Test each part of ray against all objects till collision
                #and save first collided ray part
                #(also add playerPos to ray pos to get where the ray really ends! :D)
                if(getCollision(xPos, yPos, _pos['x']+rayX, _pos['y']+rayY)):
                    #WALL
                    if(_y[x] in WALL):
                        return _y[x]


    return ' '

def getCollision(x,y, itemX, itemY):
    lowerBoundX = pieceSize*x - pieceSize/2
    upperBoundX = pieceSize*x + pieceSize/2

    lowerBoundY = pieceSize*y - pieceSize/2
    upperBoundY = pieceSize*y + pieceSize/2
     
    collision = False
    if(itemX >= lowerBoundX and itemX <= upperBoundX):
        if(itemY >= lowerBoundY and itemY <= upperBoundY):
            collision = True

    return collision

def borderDraw(win,winX,winY):
    #win.addstr(0,0,"#")
    #win.addstr(winY-2,winX-2,"#")
    
    for x in range(0,winX-2):
        win.addstr(0,x,"#")
        win.addstr(winY-2,x,"#")
    for y in range(0,winY-2):
        win.addstr(y,0,"#")
        win.addstr(y,winX-2,"#")

def viewPrinting(win,winX,winY,view):
    global cNum

    screenWidth = int(winX-1)
    midY = int(winY/2)

    #linePerRay
    LPR = screenWidth / FOV

    lastValue = 0
    for rayIndex in range(FOV):
        actualValue = int(LPR*rayIndex)

        for i in range(actualValue-lastValue):
            for z in range(int(midY - view[rayIndex][1]/10)):
                xxx = lastValue + i

                #strop??
                if(z >= midY):
                    break
                
                if(view[rayIndex][0] in WALL):
                    if(view[rayIndex][1] < 100):
                        win.addstr(int(midY) + z, xxx+1, '#', C.A_BOLD)
                        win.addstr(int(midY) - z, xxx+1, '#', C.A_BOLD)
                    elif(view[rayIndex][1] < 200):
                        win.addstr(int(midY) + z, xxx+1, '#')
                        win.addstr(int(midY) - z, xxx+1, '#')
                    elif(view[rayIndex][1] < PVD):
                        win.addstr(int(midY) + z, xxx+1, '#', C.A_DIM)
                        win.addstr(int(midY) - z, xxx+1, '#', C.A_DIM)
                else:
                    win.addstr(int(midY) + z, xxx+1, ' ')
                    win.addstr(int(midY) - z, xxx+1, ' ')
        lastValue = actualValue

def getMap(playerPos):
    actMap = []
    for y in range(len(playMap)):
        row = []
        _y = list(playMap[y])

        for x in range(len(_y)):
            if(getCollision(x,y,playerPos['x'],playerPos['y'])):
                _playerPX = x
                _playerPY = y
                row += 'O'
            elif(_y[x] == '.'):
                row += ' '
            else:
                row += str(_y[x])

        actMap += [row]


    if(315 < playerDir or playerDir < 45):
        actMap[_playerPX+1][_playerPY] = '-'
    if(45 < playerDir and playerDir < 135):
        actMap[_playerPX][_playerPY+1] = '|'
    if(135 < playerDir and playerDir < 225):
        actMap[_playerPX-1][_playerPY] = '-'
    if(225 < playerDir and playerDir < 315):
        actMap[_playerPX][_playerPY-1] = '|'


    return actMap

def getch():
    # https://www.jonwitts.co.uk/archives/896
    # adapted from https://github.com/recantha/EduKit3-RC-Keyboard/blob/master/rc_keyboard.py
    #
    # Works well better than Curses getch (lag on input - pressing even if no
    # input is being done!)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd,termios.TCSADRAIN,old_settings)
    return ch

def inputHandling(key):
    global playerPos, playerDir

    if(key in inputKeys):
        if(inputKeys[key] == 'forward'):

            moveX = (int(PMS*math.sin(math.radians(playerDir))))
            moveY = (int(PMS*math.cos(math.radians(playerDir))))

            playerPos['x'] += moveX
            playerPos['y'] += moveY

        if(inputKeys[key] == 'backward'):

            moveX = (int(PMS*math.sin(math.radians(playerDir))))
            moveY = (int(PMS*math.cos(math.radians(playerDir))))

            playerPos['x'] -= moveX
            playerPos['y'] -= moveY

        if(inputKeys[key] == 'left'):

            playerDir -= PRS
            if(playerDir < 0):
                playerDir = 360 + playerDir 

            if(playerDir >= 360):
                playerDir = playerDir - 360

        if(inputKeys[key] == 'right'):
            
            playerDir += PRS
            if(playerDir < 0):
                playerDir = 360 + playerDir 

            if(playerDir >= 360):
                playerDir = playerDir - 360

def mainProgram():
    win = C.initscr()

    # DRAWPHASE 0
    # INPUTPHASE 1
    PHASE = 0

    GAMERUNNING = True
    
    INPUT = False
    key = ''

    C.start_color()
    C.use_default_colors()
    
    #color pairs
    C.init_pair(0, C.COLOR_WHITE, -1)
    C.init_pair(1, C.COLOR_WHITE, -1)
    C.init_pair(2, C.COLOR_WHITE, -1)

    # hide cursor
    C.noecho()
    C.cbreak()
    C.curs_set(0)

    win.clear()
    win.refresh()
    
    while GAMERUNNING:
        if(PHASE == 0):
            ### DRAW LOOP
            win.clear()

            #16:9
            #winY = int(win.getmaxyx()[0])
            #winX = int((winY/9) * 16)

            winX = int(win.getmaxyx()[1])
            winY = int(win.getmaxyx()[0])
            global FOV
            #FOV = winX-2


            #displayBorder draw
            borderDraw(win,winX,winY)
            
            #get view output from displaying(raycasting)
            view = displaying(playerPos,playerDir)

            #display all from rayCast (walls and stuff)
            viewPrinting(win,winX,winY,view)            

            win.addstr(13,13,str(R.randint(0,9)))

            #if(INPUT):
            #    win.addstr(6,6,str(key))
            #    INPUT = False

            #win.addstr(5,5,"DRAWPHASE")
            win.addstr(3,3,"POS: X:{} Y:{}".format(playerPos['x'],playerPos['y']))
            win.addstr(4,3,"DIR: {}".format(playerDir))
            rootP = 5
            #mmmMap = getMap(playerPos)

            #C.endwin()
            #C.echo()
            #C.curs_set(0)

            ''' jjjjj
            for i in range(len(playMap)):
                for x in range(len(playMap[i])):
                    win.addstr(rootP + i, 3+x, mmmMap[x][i])
                    #print(mmmMap[x][i],end='')
                #print()

            #print(playMap)

            #quit()
            '''

            PHASE = 1
            win.refresh()
            ### DRAW LOOP

        elif(PHASE == 1):
            ### INPUT LOOP
            win.addstr(5,5,"INPUTPHASE")
            key = getch()
            inputHandling(key)
            if(key == 'P'):
                GAMERUNNING = False

            #INPUT = True
            PHASE = 0

    C.endwin()
    C.echo()
    C.curs_set(0)


    #if(inpThread.is_alive()):
    #    GAMERUNNING = False
    #    run_q.put(GAMERUNNING)

    #    inpThread.join()

    C.echo()
    C.endwin()

for y in range(len(playMap)):
    _y = list(playMap[y])

    for x in range(len(_y)):
        if(_y[x] == '.'):
            playerPos['y'] = (pieceSize*y)
            playerPos['x'] = (pieceSize*x)


#displaying(playerPos,playerDir)
#quit()

mainProgram()
