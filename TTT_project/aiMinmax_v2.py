#!/usr/bin/env python3

#from boardClass import BoardClass as bc
import boardClass as _bc
import time
import numpy as np
import random as r
from tqdm import tqdm


bc = _bc.BoardClass()
bc.fileReady()

def nonlin(x, deriv=False):
    if(deriv):
        return (x*(1-x))

    return 1/(1+np.exp(-x))

def netTraining(_board, player, log=False):
    #start = time.time()

    if(player == 1):
        board = _board.copy()
    else:
        board = []
        for i in range(9):
            if(_board[i] == 0.5):
                board.append(0.5)
            elif(_board[i] == 1):
                board.append(0)
            else:
                board.append(1)

    opts = bc.getMoveOptions(board, player)
    mmvals = [bc.minMax(x, player) for x in opts]

    wantedOut = [0 for i in range(9)]
    takenValue = 0

    for i in range(9):
        if(board[i] != 0.5):
            takenValue += 1
        elif(mmvals[i-takenValue] == max(mmvals)):
            wantedOut[i] = 1

    global w1, w2, b1, b2

    l1 = np.array([board])
    mid1 = np.dot(l1,w1)-b1
    l2 = nonlin(mid1)
    mid2 = np.dot(l2,w2)-b2
    l3 = nonlin(mid2)

    l3_error = np.array([wantedOut]) - l3
    l3_delta = l3_error*nonlin(l3, deriv=True)
    l2_error = l3_delta.dot(w2.T)
    l2_delta = l2_error*nonlin(l2, deriv=True)

    w2 += l2.T.dot(l3_delta)
    w1 += l1.T.dot(l2_delta)

    global avg, loopCount
    loopCount += 1
    if(loopCount == 500):
        np.save("w1File", w1)
        np.save("w2File", w2)
        np.save("b1File", b1)
        np.save("b2File", b2)
        loopCount = 0
        tqdm.write("np files saved")

    #end = time.time()
    if(log):
        #tqdm.write("Was working for {:3f}".format(end-start))
        #tqdm.write(str(np.mean(np.abs(l3_error))))
        avg += np.mean(np.abs(l3_error))

def netPlay(_board, player):

    if(player == 1):
        board = _board.copy()
    else:
        board = []
        for i in range(9):
            if(_board[i] == 0.5):
                board.append(0.5)
            elif(_board[i] == 1):
                board.append(0)
            else:
                board.append(1)

    l1 = np.array([board])
    mid1 = np.dot(l1, w1)-b1
    l2 = nonlin(mid1)
    mid2 = np.dot(l2, w2)-b2
    l3 = nonlin(mid2)

    out = list(l3[0])

    for i in range(9):
        if(board[i] != 0.5):
            out[i] = 0

    print("out")
    for y in range(3):
        print("-------")
        print("|", end="")

        for x in range(3):
            if(_board[x+(y*3)] != 0.5):
                print("    X|", end="")
            else:
                print("{:1.3f}|".format(out[x+(y*3)]), end="")

        print("")
    print("")

    _board[out.index(max(out))] = player

def humPlay(board, player):
    while True:
        try:
            pos = int(input("Select position 1-9: "))

            if(pos > 0 and pos < 10):
                if(board[pos - 1] == 0.5):
                    pos -= 1
                    break
            else:
                print("INVALID INPUT!\n")
                pass

        except ValueError:
            print("INVALID INPUT!\n")

    board[pos] = player

def gameDecisionTree():
    decision = ""

    while True:
        try:
            print()
            a = int(input("Training ---- > 1\n"+
                          "Game -------- > 2\n"+
                          "\n"+
                          "(Delete saved files -> 101)\n"+
                          "EXIT -------- > 3\n"))

            if(a > 0 and a < 4):
                a -= 1
                break
            elif(a == 101):
                while True:
                    try:
                        s = input("Are you sure (Y/N)")
                        if(s == "Y" or s == "y"):
                            global w1, w2

                            _w1 = 2*np.random.random([9, 81]) - 1
                            _w2 = 2*np.random.random([81, 9]) - 1

                            w1 = _w1
                            w2 = _w2

                            np.save("w1File", w1)
                            np.save("w2File", w2)

                            print("Weights were randomized")
                            break
                        elif(s == "N" or s == "n"):
                            print("Weights kept as before")
                            break
                        else:
                            print("INVALID INPUT!\n")
                    except ValueError:
                        print("INVALID INPUT!\n")
            else:
                pass

        except ValueError:
            print("INVALID INPUT!\n")

    if(a == 0):
        decision += "0|"

        endFound = False
        sec = True

        while True:
            if(sec):
                while True:
                    try:
                        c = input("\nWanted training time (s): ")
                        if(c == "m" or c == "M"):
                            sec = False
                            break
                        else:
                            c = int(c)

                        if(c > 0):
                            endFound = True
                            break
                        else:
                            print("INVALID INPUT!\n")
                            pass
                    except ValueError:
                        print("INVALID INPUT!\n")
            else:
                while True:
                    try:
                        c = input("\nWanted training time (m): ")
                        if(c == "s" or c == "S"):
                            sec = True
                            break
                        else:
                            c = int(c)

                        if(c > 0):
                            c *= 60
                            endFound = True
                            break
                        else:
                            print("INVALID INPUT!\n")
                            pass
                    except ValueError:
                        print("INVALID INPUT!\n")

            if(endFound):
                break
            else:
                pass

        while True:
            try:
                d = int(input("\nPseudo-random play chance (%): "))

                if(d > 0 and d < 101):
                    break
                else:
                    print("INVALID INPUT!\n")
                    pass
            except ValueError:
                print("INVALID INPUT!\n")

        decision += "0|"
        decision += str(c)+"|"+str(d)

    elif(a == 1):
        decision += "1|"
        while True:
            try:
                b = int(input("\nHow many games do you want to play?\n"))
                break
            except ValueError:
                print("INVALID INPUT!\n")

        decision += str(b)
        decision += "|0|0"

    elif(a == 2):
        decision = "exit"

    return decision

# netStructure
# 9 input
# 81 hidden
# 9 output
def loadNetWeights():
    try:
        _w1 = np.load("w1File.npy")
        _w2 = np.load("w2File.npy")
        _b1 = np.load("b1File.npy")
        _b2 = np.load("b2File.npy")
        print("Save files found - Weights loaded from files")
    except FileNotFoundError:
        _w1 = 2*np.random.random((9, 81)) - 1
        _b1 = 2*np.random.random((81)) - 1
        _w2 = 2*np.random.random((81, 9)) - 1
        _b2 = 2*np.random.random((9)) - 1
        print("No save files found - Weights initialized")

    return _w1, _w2, _b1, _b2

'''
def setUpWork():
    if(decision == "exit"):
        #break
        raise EOFError
        pass
    else:
        if(decision.split("|")[0] == "0"):
            _TRAINING = True
        else:
            _TRAINING = False

        if(decision.split("|")[1] != "0"):
            _wantedLoop = int(decision.split("|")[1])
        else:
            _wantedLoop = 1234567890

        if(decision.split("|")[2] != "0"):
            _endTime = int(decision.split("|")[2])
        else:
            _endTime = 1234567890

        if(decision.split("|")[3] != "0"):
            _ppChance = int(decision.split("|")[3])
        else:
            _ppChance = 0

    global TRAINING, wantedLoop, endTime, ppChance

    TRAINING = _TRAINING
    wantedLoop = _wantedLoop
    endTime = _endTime
    ppChance = _ppChance
'''

w1, w2, b1, b2 = loadNetWeights()

logEnabled = True
avg = 0
loopCount = 0

iter = int(input("How many training rounds? "))
for gen in range(iter):
    avg = 0
    for i in tqdm(range(bc.playCount)):
        board = bc.conv2Board(bc.getPlayBoard(i))
        c = 0
        n = 0
        for i in range(9):
            if(board[i] == 1):
                c+=1
            elif(board[i] == 0):
                n+=1

        if(n > c):
            netTraining(board,1,logEnabled)
        else:
            netTraining(board,0,logEnabled)

    if(logEnabled):
        tqdm.write("Average error in last generation: {}\n".format(avg/bc.playCount))

'''
# 1 Play - 0 Training / Loop amount / Time amount
decision = gameDecisionTree()

trainingScore = [0, 0, 0]

wantedLoop = 0
endTime = 0
ppChance = 0
setUpWork()

TURN = 0
playerHum = 1
playerAi = 0

iterations = 0
startTime = time.time()

while ((time.time() - startTime < endTime and endTime != 1234567890) or
    (iterations < wantedLoop and wantedLoop != 1234567890)):

    iterations += 1
    print("--------Iteration {}-------".format(iterations))

    TURN = 0

    board = bc.initBoard()
    while True:
        bc.printBoard(board)

        if(bc.isComplete(board)):
            if(bc.pWon(board) == playerAi):
                print("AI won")
                trainingScore[1] += 1
            elif(bc.pWon(board) == playerHum):
                print("Player won")
                trainingScore[0] += 1
            else:
                print("Draw")
                trainingScore[2] += 1

            break

        if(TURN == playerAi):
            print("PlayingAI")

            if(TRAINING):
                netTraining(board, playerAi)
            else:
                netPlay(board, playerAi)

            TURN = playerHum

        else:
            print("PlayingHuman/Random")

            if(TRAINING):
                # randomPlay(board, playerHum)
                pseudoRandomPlay(board, playerHum, ppChance)
            else:
                humPlay(board, playerHum)

            TURN = playerAi

    if(playerHum == 1):
        playerHum = 0
    else:
        playerHum = 1

    if(playerAi == 1):
        playerAi = 0
    else:
        playerAi = 1

if(TRAINING):
    print("------------------- END OF TRAINING -------------------")
    print("Player wins: {}\nAI wins: {}\nDraws: {}".format(trainingScore[0],trainingScore[1],trainingScore[2]))
    print("Work time: {:.3f}".format(time.time()-startTime))
else:
    print("\nPlayer wins: {}\nAI wins: {}\nDraws: {}".format(trainingScore[0],trainingScore[1],trainingScore[2]))
'''
input()

'''
bc.fileReady()

playerHum = 1
playerAi = 0

board = bc.initBoard()

board[1] = 0
board[4] = 1
board[0] = 0
print(board)
poss = bc.getMoveOptions(board, playerHum)

vals = []
start = time.time()

for x in poss:
    vals.append(bc.minMax(x, playerHum))

end = time.time()
print("Working for {}".format(end-start))
print(vals)
bc.printBoard(vals,board)
'''