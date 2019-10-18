#All valid phrases used to call this function
callPhrases = ["snake"]

from importlib import reload
import os
import random
#This string will be sent to users when they type "help <callPhrase>"
usageInstructions = ("Snake around and kill time.\n'snake new' to start a game")

isOver = False

def generateResponse(tailSMS, adminStatus, userName, relationalEmail, driver):
    global isOver
    isOver = False
    #create game state file using userName
    #use responses to update game state
    #after each movement check for game end, if it hits wall or self
    userName = userName.lower()
    direction = tailSMS.lower()
    print(direction)
    if((direction == "up" or direction == "down" or direction == "left" or direction == "right") and (gameExists(userName))):
        checkIfDead(direction, userName)
    elif(direction == "new"):
        buildFromFile(direction, userName)
    else:
        return("Invalid input or no current game file.\n'snake new' to start a new game.\n|up|down|left|right| are valid arguments")
    if(isOver):
        score = str(count0s(userName)-1)
        deleteGameFile(userName)
        return "GAME OVER\nYour Score: " + score + "\nType \'snake new\' to try again"
    else:
        return retBoard(userName)

def buildFromFile(direction, userName):
    #TODO change to remove both ".."s later
#    os.create("../storage/gamestates/snake/game" + userName + ".py")
    pathToFile = "storage/gamestates/snake/snake_" + userName + ".py"
    file = open(pathToFile,"w+")
    initialBoard = [["_","_","_","_","_","_"],
                    ["_","_","_","_","_","_"],
                    ["_","_","_","_","_","_"],
                    ["_","_","_","o","e","e"],
                    ["_","_","_","_","_","_"],
                    ["_","_","_","_","_","_"]]
    initialTail = [35,34]
    ax = random.randrange(5)
    ay = random.randrange(5)
    while(initialBoard[ax][ay] == "o" or initialBoard[ax][ay] == "e"):
        ax = random.randrange(5)
        ay = random.randrange(5)
    initialBoard[ax][ay] = "*"
    file.write("board = " + str(formatBoard(initialBoard)))
    file.write("\n\ntail = " + str(formatArray(initialTail)))
    file.close()

def checkIfDead(direction, userName):
    global isOver
    headLoc = headLocation(userName)
    x = int(headLoc/10)
    y = int(headLoc - x*10)

    if(direction == "right"):
        if(y+1 > 5 or isDeathMove(x, y+1, userName)):
            isOver = True
    elif(direction == "left"):
        if(y-1 < 0 or isDeathMove(x, y-1, userName)):
            isOver = True
    elif(direction == "down"):
        if(x+1 > 5 or isDeathMove(x+1, y, userName)):
            isOver = True
    elif(direction == "up"):
        if(x-1 < 0 or isDeathMove(x-1, y, userName)):
            isOver = True
    if(not isOver):
        updateBoard(direction, userName)

def count0s(userName):
    board = getBoard(userName)
    count = 0
    for x in range(len(board)):
        for y in range(len(board[x])):
            if (board[x][y] == "e"):
                count += 1
    return count

def headLocation(userName):
    board = getBoard(userName)
    for x in range(len(board)):
        for y in range(len(board[x])):
            if (board[x][y] == "o"):
                return x*10 + y


def isDeathMove(x, y, userName):
    board = getBoard(userName)
    if(board[x][y] == "e"):
        return True
    return False

def updateGameFile(userName, board, tail):
    deleteGameFile(userName)
    pathToFile = "storage/gamestates/snake/snake_" + userName + ".py"
    file = open(pathToFile,"w+")
    file.write("board = " + str(formatBoard(board)))
    file.write("\n\ntail = " + str(formatArray(tail)))
    file.close

def updateBoard(direction, userName):
    headLoc = headLocation(userName)
    x = int(headLoc/10)
    y = int(headLoc-x*10)

    tail = getTail(userName)
    board = getBoard(userName)

    tx = int(tail[0]/10)
    ty = int(tail[0]-tx*10)

    board[x][y] = "e"

    if(direction == "right"):
        tail.append(x*10+y)
        if(board[x][y+1] == "*"): #got an apple
            newApple = appleGen(userName)
            ax = int(newApple/10)
            ay = int(newApple-ax*10)
            board[ax][ay] = "*"
        else:
            tail.pop(0)
            board[tx][ty] = "_"
        board[x][y+1] = "o"

    elif(direction == "left"):

        tail.append(x*10+y)
        if(board[x][y-1] == "*"): #got an apple
            newApple = appleGen(userName)
            ax = int(newApple/10)
            ay = int(newApple-ax*10)
            board[ax][ay] = "*"
        else:
            tail.pop(0)
            board[tx][ty] = "_"
        board[x][y-1] = "o"

    elif(direction == "down"):

        tail.append(x*10+y)
        if(board[x+1][y] == "*"): #got an apple
            newApple = appleGen(userName)
            ax = int(newApple/10)
            ay = int(newApple-ax*10)
            board[ax][ay] = "*"
        else:
            tail.pop(0)
            board[tx][ty] = "_"
        board[x+1][y] = "o"

    elif(direction == "up"):

        tail.append(x*10+y)
        if(board[x-1][y] == "*"): #got an apple
            newApple = appleGen(userName)
            ax = int(newApple/10)
            ay = int(newApple-ax*10)
            board[ax][ay] = "*"
        else:
            tail.pop(0)
            board[tx][ty] = "_"
        board[x-1][y] = "o"

    updateGameFile(userName, board, tail)

    #move head, replace old head with o, clear last o if it does not eat an apple, if it did eat then generate new apple, if board is full then print win
def retBoard(userName):
    string = boardToString(getBoard(userName))
    return(string)

def appleGen(userName):
    board = getBoard(userName)
    ax = random.randrange(5)
    ay = random.randrange(5)
    while(board[ax][ay] == "o" or board[ax][ay] == "e"):
        ax = random.randrange(5)
        ay = random.randrange(5)
    return ax*10+ay

def boardToString(board):
    resultString = ""
    for i in range(len(board)):
        for j in range(len(board[i])):
            resultString += (str(board[i][j]) + "   ")
        resultString += "\n"

    return resultString



def getTail(userName):
    exec("import storage.gamestates.snake.snake_" + userName + " as " + "snake_" + userName)
    exec ("reload(snake_" + userName + ")")
    return eval("snake_" + userName + ".tail")

def getBoard(userName):
    exec("import storage.gamestates.snake.snake_" + userName + " as " + "snake_" + userName)
    exec ("reload(snake_" + userName + ")")
    return eval("snake_" + userName + ".board")

def gameExists(userName):
    for file in os.listdir("storage/gamestates/snake"):
        if(file.endswith(userName + ".py")):
            return True
    return False

def formatBoard(inputBoard):
    boardString = "["
    for i in range(len(inputBoard)):
        boardString += ("[")
        for j in range(len(inputBoard[i])):
            boardString += ("\"")
            boardString += str("".join(inputBoard[i][j]))
            if (j != len(inputBoard[i]) - 1):
                boardString += ("\",")
            else:
                boardString += ("\"")
        if(i != len(inputBoard)- 1):
            boardString += ("],\n\t\t")
        else:
            boardString += ("]")
    boardString += "]"
    return boardString

def formatArray(inputArray):
    arrayString = "["
    for i in range(len(inputArray)):
        arrayString += str(inputArray[i])
        if(i != len(inputArray) - 1):
            arrayString += (",")
    arrayString += "]"
    return arrayString

def deleteGameFile(userName):
    os.remove("storage/gamestates/snake/snake_" + userName + ".py")

#CHECK IF VALID input
#BUILD FROM file
#CHECK IF INPUT RESULTS IN LOSE
#IF NOT, UPDATE BOARD BASED OFF OF INPUT
#KEEP TRACK OF NUMBER OF O'S AS SCORE
