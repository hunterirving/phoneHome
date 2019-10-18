callPhrases = ["chess"]

usageInstructions = ("Usage:\nchess <from>-<to>\nex: \"chess A1-H8\""
    "\n\"chess O-O-O\""
    "\n\nOther Commands:\nchess challenge <user>\nchess challenge computer"
    "\nchess accept\nchess forfeit\nchess state")

import os
from random import shuffle
import sys
from phoneHome import sendResponse
from users import users as users
import re
from importlib import reload

def generateResponse(tailSMS, adminStatus, userName, relationalEmail, driver):
    if(tailSMS == ""):
        return badCommand()
    else:
        splitTail = tailSMS.split()
        if(splitTail[0].lower() == "challenge"):
            if(len(splitTail) != 2):
                return badCommand()
            elif(splitTail[1].lower() == userName.lower() and findGameFile(userName) == ""):
                return "You cannot challenge yourself"
            elif(findGameFile(userName) == ""):
                if(splitTail[1].lower() == "computer"):
                    createGameFile(userName, "Computer")
                else:
                    for i in range(len(users)):
                        if(splitTail[1].lower() == users[i][1].lower()):
                            if(findGameFile(users[i][1]) == ""):
                                createGameFile(userName, users[i][1])

                                opponentsFakeEmail = users[i][0]
                                sendResponse(opponentsFakeEmail, (userName + " has challenged you to a game of chess. Reply \"chess accept\" to accept or \"chess forfeit\" to forfeit."), driver)
                                return("Challenged " + users[i][1] + " to a game of chess. Awaiting response from " + users[i][1] + ".")
                            else:
                                gameFile = findGameFile(users[i][1])
                                gameStarted = getGameStarted(gameFile)
                                returnString = ""
                                if not gameStarted:
                                    returnString = (users[i][1]
                                        + " has already been challenged to a game of chess by "
                                        +  getOtherUser(users[i][1]) + ".")
                                else:
                                    returnString = (users[i][1] + " is already in a game of chess with "
                                    + getOtherUser(users[i][1]) + ".")
                                returnString += ("\n\nYou can message "
                                    + users[i][1]
                                    + " using the \"msg\" command.")
                                return returnString

                    else:
                        return ("User \"" + splitTail[1]
                            + "\" not found. "
                            + "\n\nInput to this module is not case-sensitive."
                            + " You can list all users using the "
                            + "\"listusers\" command.")
            else:
                gameFile = findGameFile(userName)
                gameStarted = getGameStarted(gameFile)
                challenger = getChallenger(gameFile)

                if not gameStarted and (challenger == userName):
                    return "You have already challenged " + getOtherUser(userName) + " to a game of chess. Reply \"chess forfeit\" to retract that challenge."
                elif not gameStarted and (challenger != userName):
                    return getOtherUser(userName) + " has challenged you to a game of chess. You must accept (\"chess accept\") or forfeit (\"chess forfeit\") that challenge before challenging other users."
                if gameStarted:
                    return "You are already in a game of chess with " + getOtherUser(userName) + ". Reply \"chess forfeit\" to leave the current game."

        elif(len(splitTail) == 1):
            if(splitTail[0].lower() == "accept"):
                if(findGameFile(userName) == ""):
                    return "There is no challenge to accept. To challenge another user to a game of chess, reply \"chess challenge <user>\"."
                else:
                    gameFile = findGameFile(userName)
                    board = getBoard(gameFile)
                    challenger = getChallenger(gameFile)
                    gameStarted = getGameStarted(gameFile)
                    opponentsUserName = getOtherUser(userName)


                    if(gameStarted):
                        return "There is no challenge to accept. You are currently in a game of chess with " + opponentsUserName + ". Reply \"chess forfeit\" to leave the current game."
                    elif(challenger == userName):
                        return "You cannot accept your own challenge. You have challenged " + opponentsUserName + " to a game of chess. Awaiting response.\n\nReply \"chess forfeit\" to retract your challenge."
                    else:
                        updateGameFile(gameFile, "", board) #start game
                        opponentsFakeEmail = getFakeEmail(opponentsUserName)
                        opponentsColor = getUserColor(opponentsUserName)
                        usersColor = getUserColor(userName)
                        sendResponse(opponentsFakeEmail, stateToString(board, "", opponentsUserName, opponentsColor), driver)

                        return stateToString(board, "", userName, usersColor)

            elif(splitTail[0].lower() == "forfeit"):
                if(findGameFile(userName) == ""):
                    return "You are not currently in a game of chess. To initiate a game with another user, reply \"chess challenge <user>\""
                else:
                    opponentsUserName = getOtherUser(userName)
                    opponentsFakeEmail = getFakeEmail(opponentsUserName)

                    sendResponse(opponentsFakeEmail, userName + " has forfeited the chess match.", driver)
                    deleteGameFile(findGameFile(userName))
                    return "You have forfeited your chess match with " + opponentsUserName + "."

            elif(splitTail[0].lower() == "state"):
                if(findGameFile(userName) == ""):
                    return "You are not currently in a game of chess. To initiate a game with another user, reply \"chess challenge <user>\""
                else:
                    gameFile = findGameFile(userName)
                    gameStarted = getGameStarted(gameFile)
                    if(not gameStarted):
                        return "You have challenged " + getOtherUser(userName) + " to a game of chess. Awaiting response.\n\nReply \"chess forfeit\" to retract your challenge."
                    else: #game IS started..
                        board = getBoard(gameFile)
                        moveWithAppendage = getMoveFromFile(gameFile)
                        userColor = getUserColor(userName)
                        return stateToString(board, moveWithAppendage, userName, userColor)

            else: #could be good input
                gameFile = findGameFile(userName)
                gameStarted = getGameStarted(gameFile)
                previousMove = getMoveFromFile(gameFile)
                print("126: movefromfile: " + previousMove)
                board = getBoard(gameFile)
                print("boardfromfile:\n" + boardToString(board))
                userColor = getUserColor(userName)
                print("userColor: " + userColor)
                playerToMoveNext = getPlayerToMoveNext(userName, userColor, previousMove)
                print("playerToMoveNext: " + playerToMoveNext)
                if(playerToMoveNext != userName):
                    if(moveIsFormattedCorrectly(tailSMS)):
                        return "It is currently " + playerToMoveNext + "'s turn. Awaiting " + playerToMoveNext + "'s move."
                    else:
                        return badCommand()
                else:
                    if(moveIsFormattedCorrectly(tailSMS)):
                        if(tailSMS.upper() in getValidMoves(userName, board, previousMove)):
                            postMoveBoard = getUpdatedBoard(tailSMS, board, userName) #180
                            updateGameFile(gameFile, (tailSMS.upper() + userColor), postMoveBoard) #seems to work..

                            #tell players move has been made
                            opponentsUserName = getOtherUser(userName)
                            opponentsColor = getUserColor(opponentsUserName)
                            opponentsFakeEmail = getFakeEmail(opponentsUserName) #seems to work.

                            #if the current user just made a move that ended the game
                            if(stateToString(postMoveBoard, tailSMS.upper() + userColor, userName, userColor).endswith("#")):
                                #other user (loser) gets checkmate-updated board
                                sendResponse(opponentsFakeEmail, stateToString(postMoveBoard, tailSMS.upper() + userColor, opponentsUserName, opponentsColor), driver)
                                #winner gets checkmate-updated board
                                sendResponse(relationalEmail, stateToString(postMoveBoard, tailSMS.upper() + userColor, userName, userColor), driver)
                                #loser gets game over
                                sendResponse(opponentsFakeEmail, "CHECKMATE. " + userName.upper() + " WINS.", driver)
                                #end the game for real
                                deleteGameFile(findGameFile(userName))
                                #winner gets "you won"
                                return "CHECKMATE. YOU WON!"

                            elif(stateToString(postMoveBoard, tailSMS.upper() + userColor, userName, userColor).endswith("=")):
                                #other user (loser) gets stalemate-updated board
                                sendResponse(opponentsFakeEmail, stateToString(postMoveBoard, tailSMS.upper() + userColor, opponentsUserName, opponentsColor), driver)
                                #winner gets stalemate-updated board
                                sendResponse(relationalEmail, stateToString(postMoveBoard, tailSMS.upper() + userColor, userName, userColor), driver)
                                #loser gets game over
                                sendResponse(opponentsFakeEmail, "STALEMATE. (TIE GAME)", driver)
                                #end the game for real
                                deleteGameFile(findGameFile(userName))
                                #winner gets "you won"
                                return "STALEMATE. (TIE GAME)"

                            else: #game is not over
                                sendResponse(opponentsFakeEmail, stateToString(postMoveBoard, tailSMS.upper() + userColor, opponentsUserName, opponentsColor), driver)

                                return stateToString(postMoveBoard, tailSMS.upper() + userColor, userName, userColor)
                        else:
                            return "\"" + tailSMS + "\" is not a valid move on the current board. Reply \"chess state\" for current game state."
                    else:
                        return badCommand()

        return badCommand()

def boardToString(board):
    resultString = ""
    for i in range(len(board)):
        for j in range(len(board[i])):
            resultString += (str(board[i][j]).replace("*","'")).replace(".",",")
        resultString += "\n"
    return resultString

def stateToString(inputBoard, moveWithAppendage, userName, userColor):
    resultString = boardToString(inputBoard) + "\n"
    if(moveWithAppendage == ""):
        if(userColor == "'"):
            resultString += "It is your (') move."
        elif(userColor == ","):
            resultString += getOtherUser(userName) + " (') will open."
    else:
        if(moveWithAppendage.endswith(userColor)):
            resultString += "Your move: " + moveWithAppendage[:-1] + getSymbol(getOtherUser(userName), inputBoard, moveWithAppendage, userName)
        else:
            resultString += getOtherUser(userName) + "'s move: " + moveWithAppendage[:-1] + getSymbol(userName, inputBoard, moveWithAppendage, getOtherUser(userName))
    return resultString

def badCommand():
    return "Invalid input to chess module. Reply \"help chess\" for usage instructions."

#attacked.....attacker
def getSymbol(userName, inputBoard, moveOpponentJustMade, attackerName):

    check = False

    opponentPotentialMoves = getPotentialMoves(inputBoard, getUserColor(attackerName), "")
    myKingSquare = getKingSquare(getUserColor(userName), inputBoard)
    for opponentPotentialMove in opponentPotentialMoves:
        if(opponentPotentialMove.endswith(myKingSquare)):
            check = True
            break
    #checkmate
    if(getValidMoves(userName, inputBoard, moveOpponentJustMade) == [] and check == True):
        return "#"
    #stalemate
    elif(getValidMoves(userName, inputBoard, moveOpponentJustMade) == [] and check == False):
        return "="
    #check
    elif(getValidMoves(userName, inputBoard, moveOpponentJustMade) != [] and check == True):
        return "+"

    return ""

def getKingSquare(playerColor, board):
    supplimentaryColor = None
    if(playerColor == "'"):
        supplimentaryColor = "*"
    elif(playerColor == ","):
        supplimentaryColor = "."

    for i in range(len(board)):
        for j in range(len(board[i])):
            if (board[i][j].startswith("K") and (board[i][j].endswith(playerColor) or board[i][j].endswith(supplimentaryColor))):
                return indexStringToMoveString("00-" + str(j) + str(i))[3:]

def findGameFile(userName):
    for file in os.listdir("storage/gamestates/chess"):
        if(file.endswith(".py") and file.startswith("game")):
            exec("import storage.gamestates.chess." + file[:-3] + " as " + file[:-3])
            exec("reload(" + file[:-3] + ")")
            for i in range(eval("len(" + file[:-3] + ".players)")):
                if(eval(file[:-3] + ".players[i][0] == \"" + userName + "\"")):
                    return file
    return ""

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

def moveIsFormattedCorrectly(tailSMS):
    upperSMS = tailSMS.upper()
    if(upperSMS == "O-O-O"): #castle
        return True
    elif(upperSMS == "O-O"): #castle
        return True
    else: #not a castle
        if(upperSMS[:-3] == upperSMS[-2:]): #check that from and to are not equal, cause that's NEVER a valid format for a move
            return False
        pattern = re.compile("[A-H]{1}[1-8]{1}-[A-H]{1}[1-8]{1}$")
        if(re.match(pattern, upperSMS) != None):
            return True
        else: #move is no good
            return False

def letterToColumnIndex(letter):
    letters = ["A","B","C","D","E","F","G","H"]
    for i in range(len(letters)):
        if letter == letters[i]:
            return i

def numberToRowIndex(number):
        numbers = ["8","7","6","5","4","3","2","1"]
        for i in range(len(numbers)):
            if number == numbers[i]:
                return i

def createGameFile(userName, challengedName):
    i = 1
    while(os.path.isfile("storage/gamestates/chess/game" + str(i) + ".py")):
        i += 1
    pathToFile = "storage/gamestates/chess/game" + str(i) + ".py"
    file = open(pathToFile,"w+")
    blackOrWhite = [",","'"]
    shuffle(blackOrWhite)

    file.write("gameStarted = False")
    file.write("\n\nplayers = [[\"" + userName + "\",\"" + blackOrWhite[0] + "\"],[\"" + challengedName + "\",\"" + blackOrWhite[1] + "\"]]")
    file.write("\n\nmostRecentMove = \"\"")
    initialBoard = [["R,","N,","B,","Q,","K,","B,","N,","R,"],
                    ["P,","P,","P,","P,","P,","P,","P,","P,"],
                    ["0-","0-","0-","0-","0-","0-","0-","0-"],
                    ["0-","0-","0-","0-","0-","0-","0-","0-"],
                    ["0-","0-","0-","0-","0-","0-","0-","0-"],
                    ["0-","0-","0-","0-","0-","0-","0-","0-"],
                    ["P'","P'","P'","P'","P'","P'","P'","P'"],
                    ["R'","N'","B'","Q'","K'","B'","N'","R'"]]

    file.write("\n\nboard = " + str(formatBoard(initialBoard)))

    file.close()
    return "game" + str(i) + ".py"

def updateGameFile(fileName, mostRecentMove, newBoardList):
    oldFilePath = "storage/gamestates/chess/" + fileName
    oldFile = open(oldFilePath, "r")
    oldFileLines = list(filter(None, [line.rstrip('\n') for line in oldFile]))
    newFilePath = ("storage/gamestates/chess/" + fileName + ".tmp")
    newFile = open(newFilePath,"w+")
    newFile.write("gameStarted = True")
    newFile.write("\n\n" + oldFileLines[1]) #players
    oldFile.close()
    newFile.write("\n\nmostRecentMove = \"" + mostRecentMove + "\"") #new "mostRecentMove"

    newFile.write("\n\nboard = " + str(formatBoard(newBoardList)))
    newFile.close()

    os.remove(oldFilePath)
    os.rename(newFilePath, oldFilePath)
    print("in updategamefile, mostrecentmove: " + mostRecentMove)
    return

def deleteGameFile(fileName):
    os.remove("storage/gamestates/chess/" + fileName)
    return
#hunter2, , lastmovemade'
def getPlayerToMoveNext(userName, userColor, moveWithAppendage):
    print("the move inside getplayertomovenext: " + moveWithAppendage)
    if(moveWithAppendage == ""):
        if userColor == "'":
            return userName
        elif userColor == ",":
            return getOtherUser(userName)

    if(moveWithAppendage.endswith(userColor)):
        return getOtherUser(userName)
    else:
        return userName

def getGameStarted(gameFile):
    exec("import storage.gamestates.chess." + gameFile[:-3] + " as " + gameFile[:-3])
    exec("reload(" + gameFile[:-3] + ")")
    return eval(gameFile[:-3] + ".gameStarted")

def getChallenger(gameFile):
    exec("import storage.gamestates.chess." + gameFile[:-3] + " as " + gameFile[:-3])
    exec("reload(" + gameFile[:-3] + ")")
    return eval(gameFile[:-3] + ".players[0][0]")

def getUpdatedBoard(tailSMS, board, userName):
    move = tailSMS.upper()
    newboard = [[board[x][y] for y in range(len(board[0]))] for x in range(len(board))]
    #print("getting updated board")
    rowIndex = None #used only in castling situations
    color = None
    if(getUserColor(userName) == "'"):
        rowIndex = 7
        color = "*"
    elif(getUserColor(userName) == ","):
        rowIndex = 0
        color = "."

    if(move == "O-O-O"): #queen's side castling
        newboard[rowIndex][2] = "K" + color #move king and mark as touched
        newboard[rowIndex][4] = "0-" #empty out old space

        newboard[rowIndex][3] = "R" + color #move rook and mark as touched
        newboard[rowIndex][0] = "0-" #empty out old space

    elif(move == "O-O"): #king's side castling
        newboard[rowIndex][6] = "K" + color #move king and mark as touched
        newboard[rowIndex][4] = "0-" #empty out old space

        newboard[rowIndex][5] = "R" + color #move rook and mark as touched
        newboard[rowIndex][7] = "0-" #empty out old space

    else: #non-castling moves
        #check to see if we have to remove an en passant captured pawn...
        if(newboard[numberToRowIndex(move[1])][letterToColumnIndex(move[0])].startswith("P")): #peice who is moving is a pawn
                if(move[0] != move[3]): #that pawn is capturing... (it moved horizontally)
                    if(newboard[numberToRowIndex(move[4])][letterToColumnIndex(move[3])] == "0-"): #capturing seemingly nothing
                        #blank out en passant captured pawn
                        newboard[numberToRowIndex(move[1])][letterToColumnIndex(move[3])] = "0-"
        #"move" peice by copying to new location (overwriting anything there) then removing from old location

        #TODO UPDATE PAWNS TO QUEENS
        #...

        newboard[numberToRowIndex(move[4])][letterToColumnIndex(move[3])] = newboard[numberToRowIndex(move[1])][letterToColumnIndex(move[0])][:-1] + color #copy peice to new location, marking as "touched"
        newboard[numberToRowIndex(move[1])][letterToColumnIndex(move[0])] = "0-" #clear old square

    return newboard

def getBoard(gameFile):
    exec("import storage.gamestates.chess." + gameFile[:-3] + " as " + gameFile[:-3])
    exec("reload(" + gameFile[:-3] + ")")
    return eval(gameFile[:-3] + ".board")

def getFakeEmail(userName):
    for i in range(len(users)):
        if(users[i][1] == userName):
            return users[i][0]

def getMoveFromFile(gameFile):
    exec("import storage.gamestates.chess." + gameFile[:-3] + " as " + gameFile[:-3])
    exec("reload(" + gameFile[:-3] + ")")
    theMove =  eval(gameFile[:-3] + ".mostRecentMove")
    return theMove

def getUserColor(userName):
    gameFile = findGameFile(userName)
    exec("import storage.gamestates.chess." + gameFile[:-3] + " as " + gameFile[:-3])
    exec("reload(" + gameFile[:-3] + ")")
    players = eval(gameFile[:-3] + ".players")
    for i in range(len(players)):
        if players[i][0] == userName:
            return players[i][1]

def getOtherUser(userName):
    gameFile = findGameFile(userName)
    exec("import storage.gamestates.chess." + gameFile[:-3] + " as " + gameFile[:-3])
    exec("reload(" + gameFile[:-3] + ")")
    for i in range(0, len(eval(gameFile[:-3] + ".players"))):
        if((eval(gameFile[:-3] + ".players")[i][0]) != userName):
            return eval(gameFile[:-3] + ".players")[i][0]

def getValidMoves(userName, board, moveOpponentJustMade):
    userColor = getUserColor(userName)
    return removeJeopardyMoves(userName, getPotentialMoves(board, userColor, moveOpponentJustMade), board)

def indexStringToMoveString(indexString):
    letters = ["A","B","C","D","E","F","G","H"]
    numbers = ["8","7","6","5","4","3","2","1"]
    fromLetter = letters[int(indexString[0])]
    fromNumber = numbers[int(indexString[1])]
    toLetter = letters[int(indexString[3])]
    toNumber = numbers[int(indexString[4])]

    return str(fromLetter + fromNumber + "-" + toLetter + toNumber)

def getPotentialMoves(board, playerColor, lastMove):
    opponentColor = None
    supplimentaryColor = None
    opponentSupColor = None
    rowIndex = None
    if(playerColor == "'"):
        supplimentaryColor = "*"
        opponentColor = ","
        opponentSupColor = "."
        rowIndex = 7
    elif(playerColor == ","):
        supplimentaryColor = "."
        opponentColor = "'"
        opponentSupColor = "*"
        rowIndex = 0

    potentialMoves = []

    for i in range(len(board)): #iterate over rows
        for j in range(len(board[i])): #iterate over cells in rows
            if(board[i][j].endswith(playerColor) or board[i][j].endswith(supplimentaryColor)): #peice is of calling user's color
                if(board[i][j].startswith("P")): #peice is a pawn of calling user's color
                    if(playerColor == "'"): #if white
                        if(i-1 in range(8)):
                            if(board[i-1][j] == "0-"): #in range and destination (1 forward) is vacant
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j) + str(i-1)))
                        if(i-2 in range(8)):
                            if(board[i][j].endswith("'") and board[i-2][j] == "0-" and board[i-1][j] == "0-"): #hasn't been "touched" yet and destination (2 forward) is vacant AND prior is vacnat
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j) + str(i-2)))
                        if(i-1 in range(8) and j-1 in range(8)): #capture left
                            if(board[i-1][j-1] != "0-" and (not board[i-1][j-1].endswith(playerColor)) and (not board[i-1][j-1].endswith(supplimentaryColor))):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-1) + str(i-1)))
                        if(i-1 in range(8) and j+1 in range(8)): #capture right
                            if(board[i-1][j+1] != "0-" and (not board[i-1][j+1].endswith(playerColor)) and (not board[i-1][j+1].endswith(supplimentaryColor))):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+1) + str(i-1)))
                        if(i == 3): #on the proper row for en passant
                            if(j-1 >= 0): #en passant left and up
                                if(board[i][j-1] == "P." and board[i-1][j-1] == "0-"): #unneccesary emptiness check
                                    if(lastMove == indexStringToMoveString(str(j-1) + str(i-2) + "-" + str(j-1) + str(i)) + ","):
                                        potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-1) + str(i-1)))
                                        #print("added en passant left and up")

                            if(j+1 <= 7): #en passant right and up
                                if(board[i][j+1] == "P." and board[i-1][j+1] == "0-"): #unneccesary emptiness check
                                    if(lastMove == indexStringToMoveString(str(j+1) + str(i-2) + "-" + str(j+1) + str(i)) + ","):
                                        potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+1) + str(i-1)))
                                        #print("added en passant right and up")
                    elif(playerColor == ","): #if black
                        if(i+1 in range(8)):
                            if(board[i+1][j] == "0-"):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j) + str(i+1))) #move forward 1 square
                        if(i+2 in range(8)):
                            if(board[i][j].endswith(",") and board[i+2][j] == "0-" and board[i+1][j] == "0-"): #not yet touched and 2 forward is vacant
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j) + str(i+2)))
                        if(i+1 in range(8) and j-1 in range(8)): #capture left
                            if(board[i+1][j-1] != "0-" and (not board[i+1][j-1].endswith(playerColor)) and (not board[i+1][j-1].endswith(supplimentaryColor))):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-1) + str(i+1)))
                        if(i+1 in range(8) and j+1 in range(8)): #capture right
                            if(board[i+1][j+1] != "0-" and (not board[i+1][j+1].endswith(playerColor)) and (not board[i+1][j+1].endswith(supplimentaryColor))):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+1) + str(i+1)))
                        if(i == 4): #on the proper row for en passant
                            if(j-1 >= 0): #en passant left and down
                                if(board[i][j-1] == "P*" and board[i+1][j-1] == "0-"): #unneccesary emptiness check
                                    if(lastMove == indexStringToMoveString(str(j-1) + str(i+2) + "-" + str(j-1) + str(i)) + "'"):
                                        potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-1) + str(i+1)))
                                        #print("added en passant left and down")
                            if(j+1 <= 7): #en passant right and down
                                if(board[i][j+1] == "P*" and board[i+1][j+1] == "0-"): #unneccesary emptiness check
                                    if(lastMove == indexStringToMoveString(str(j+1) + str(i+2) + "-" + str(j+1) + str(i)) + "'"):
                                        potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+1) + str(i+1)))
                                        #print("added en passant right and down")

                if(board[i][j].startswith("R") or board[i][j].startswith("Q")): #peice is a rook (OR QUEEN) of calling user's color
                    #moving up
                    ii = i - 1
                    while(ii >= 0):
                        if(board[ii][j] == "0-"):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j) + str(ii)))
                            ii = ii - 1
                            continue
                        elif(board[ii][j].endswith(playerColor) or board[ii][j].endswith(supplimentaryColor)):
                            break
                        elif(board[ii][j].endswith(opponentColor) or board[ii][j].endswith(opponentSupColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j) + str(ii))) #potential capture
                            break
                    #moving right
                    jj = j + 1
                    while(jj <= 7):
                        if(board[i][jj] == "0-"):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(i)))
                            jj = jj + 1
                        elif(board[i][jj].endswith(playerColor) or board[i][jj].endswith(supplimentaryColor)):
                            break
                        elif(board[i][jj].endswith(opponentColor) or board[i][jj].endswith(opponentSupColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(i)))
                            break
                    #moving down
                    ii = i + 1
                    while(ii <= 7):
                        if(board[ii][j] == "0-"):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j) + str(ii)))
                            ii = ii + 1
                            continue
                        elif(board[ii][j].endswith(playerColor) or board[ii][j].endswith(supplimentaryColor)):
                            break
                        elif(board[ii][j].endswith(opponentColor) or board[ii][j].endswith(opponentSupColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j) + str(ii))) #potential capture
                            break
                    #moving left
                    jj = j - 1
                    while(jj >= 0):
                        if(board[i][jj] == "0-"):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(i)))
                            jj = jj - 1
                        elif(board[i][jj].endswith(playerColor) or board[i][jj].endswith(supplimentaryColor)):
                            break
                        elif(board[i][jj].endswith(opponentColor) or board[i][jj].endswith(opponentSupColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(i)))
                            break

                if(board[i][j].startswith("N")): #peice is a (k)night of calling user's color
                    #top inner
                    if(i-2 >= 0):
                        if(j-1 >= 0):
                            if not(board[i-2][j-1].endswith(playerColor) or board[i-2][j-1].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-1) + str(i-2)))
                        if(j+1 <= 7):
                            if not(board[i-2][j+1].endswith(playerColor) or board[i-2][j-1].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+1) + str(i-2)))
                    #top outer
                    if(i-1 >= 0):
                        if(j-2 >= 0):
                            if not(board[i-1][j-2].endswith(playerColor) or board[i-2][j-1].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-2) + str(i-1)))
                        if(j+2 <= 7):
                            if not(board[i-1][j+2].endswith(playerColor) or board[i-2][j-1].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+2) + str(i-1)))
                    #bottom inner
                    if(i+2 <= 7):
                        if(j-1 >= 0):
                            if not(board[i+2][j-1].endswith(playerColor) or board[i-2][j-1].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-1) + str(i+2)))
                        if(j+1 <= 7):
                            if not(board[i+2][j+1].endswith(playerColor) or board[i-2][j-1].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+1) + str(i+2)))
                    #bottom outer
                    if(i+1 <= 7):
                        if(j-2 >= 0):
                            if not(board[i+1][j-2].endswith(playerColor) or board[i+1][j-2].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-2) + str(i+1)))
                        if(j+2 <= 7):
                            if not(board[i+1][j+2].endswith(playerColor) or board[i+1][j-2].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+2) + str(i+1)))

                if(board[i][j].startswith("B") or board[i][j].startswith("Q")): #peice is a bishop (or QUEEN) of calling user's color
                    #left & down
                    ii = i + 1
                    jj = j - 1
                    while(ii <= 7 and jj >= 0):
                        if(board[ii][jj] == "0-"):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(ii)))
                            ii = ii + 1
                            jj = jj - 1
                        elif(board[ii][jj].endswith(playerColor) or board[ii][jj].endswith(supplimentaryColor)):
                            break
                        elif(board[ii][jj].endswith(opponentColor) or board[ii][jj].endswith(opponentSupColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(ii)))
                            break
                    #left & up
                    ii = i - 1
                    jj = j - 1
                    while(ii >= 0 and jj >= 0):
                        if(board[ii][jj] == "0-"):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(ii)))
                            ii = ii - 1
                            jj = jj - 1
                        elif(board[ii][jj].endswith(playerColor) or board[ii][jj].endswith(supplimentaryColor)):
                            break
                        elif(board[ii][jj].endswith(opponentColor) or board[ii][jj].endswith(opponentSupColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(ii)))
                            break
                    #right & up
                    ii = i - 1
                    jj = j + 1
                    while(ii >= 0 and jj <= 7):
                        if(board[ii][jj] == "0-"):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(ii)))
                            ii = ii - 1
                            jj = jj + 1
                        elif(board[ii][jj].endswith(playerColor) or board[ii][jj].endswith(supplimentaryColor)):
                            break
                        elif(board[ii][jj].endswith(opponentColor) or board[ii][jj].endswith(opponentSupColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(ii)))
                            break
                    #right & down
                    ii = i + 1
                    jj = j + 1
                    while(ii <= 7 and jj <= 7):
                        if(board[ii][jj] == "0-"):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(ii)))
                            ii = ii + 1
                            jj = jj + 1
                        elif(board[ii][jj].endswith(playerColor) or board[ii][jj].endswith(supplimentaryColor)):
                            break
                        elif(board[ii][jj].endswith(opponentColor) or board[ii][jj].endswith(opponentSupColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(jj) + str(ii)))
                            break
                if(board[i][j].startswith("K")): #peice is the calling user's king
                    #up
                    if(i-1 >= 0):
                        #strictly up
                        if not(board[i-1][j].endswith(playerColor) or board[i-1][j].endswith(supplimentaryColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j) + str(i-1)))
                        #up and right
                        if(j+1 <= 7):
                            if not(board[i-1][j+1].endswith(playerColor) or board[i-1][j+1].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+1) + str(i-1)))
                        #up and left
                        if(j-1 >= 0):
                            if not(board[i-1][j-1].endswith(playerColor) or board[i-1][j-1].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-1) + str(i-1)))
                    #down
                    if(i+1 <= 7):
                        #strictly down
                        if not(board[i+1][j].endswith(playerColor) or board[i+1][j].endswith(supplimentaryColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j) + str(i+1)))
                        #down and right
                        if(j+1 <= 7):
                            if not(board[i+1][j+1].endswith(playerColor) or board[i+1][j+1].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+1) + str(i+1)))
                        #down and left
                        if(j-1 >= 0):
                            if not(board[i+1][j-1].endswith(playerColor) or board[i+1][j-1].endswith(supplimentaryColor)):
                                potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-1) + str(i+1)))
                    #left
                    if(j-1 >= 0):
                        #strictly left
                        if not(board[i][j-1].endswith(playerColor) or board[i][j-1].endswith(supplimentaryColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j-1) + str(i)))
                    #right
                    if(j+1 <= 7):
                        #strictly right
                        if not(board[i][j+1].endswith(playerColor) or board[i][j+1].endswith(supplimentaryColor)):
                            potentialMoves.append(indexStringToMoveString(str(j) + str(i) + "-" + str(j+1) + str(i)))
                    if(board[i][j].endswith(playerColor)): #that is, the king has not been "touched"
                        #Queen-side castling (O-O-O)
                        if(board[rowIndex][0].startswith("R") and board[rowIndex][0].endswith(playerColor)): #involved rook is "untouched"; check for ROOK unnecessary in real chess game
                            if(board[rowIndex][1] == "0-" and board[rowIndex][2] == "0-" and board[rowIndex][3] == "0-"): #required spaces are clear
                                potentialMoves.append("O-O-O")
                        #King-side castling (O-O)
                        if(board[rowIndex][7].startswith("R") and board[rowIndex][7].endswith(playerColor)):
                            if(board[rowIndex][5] == "0-" and board[rowIndex][6] == "0-"):
                                potentialMoves.append("O-O")
    return potentialMoves

def removeJeopardyMoves(userName, potentialMoves, preMoveBoard):
    validMoves = potentialMoves[:]
    kingDefault = None
    kingLeftOne = None
    kingLeftTwo = None
    kingRightOne = None
    kingRightTwo = None

    if(getUserColor(userName) == "'"):
        kingDefault = "E1"
        kingLeftOne = "D1"
        kingLeftTwo = "C1"
        kingRightOne = "F1"
        kingRightTwo = "G1"
    elif(getUserColor(userName) == ","):
        kingDefault = "E8"
        kingLeftOne = "D8"
        kingLeftTwo = "C8"
        kingRightOne = "F8"
        kingRightTwo = "G8"

    #castling validity check
    for i in range(len(potentialMoves)):
        #check that squares king is passing through are safe
        if(potentialMoves[i] == "O-O-O"):
            opponentPotentialMoves = getPotentialMoves(preMoveBoard, getUserColor(getOtherUser(userName)), "")
            for opponentPotentialMove in opponentPotentialMoves:
                if(opponentPotentialMove.endswith((kingDefault, kingLeftOne, kingLeftTwo))):

                    validMoves.remove("O-O-O")
                    break
            continue
        elif(potentialMoves[i] == "O-O"):
            opponentPotentialMoves = getPotentialMoves(preMoveBoard, getUserColor(getOtherUser(userName)), "")
            for opponentPotentialMove in opponentPotentialMoves:
                if(opponentPotentialMove.endswith((kingDefault, kingRightOne, kingRightTwo))):

                    validMoves.remove("O-O")
                    break
            continue

        #a hypothetical board where we made the move in question...
        potentialBoard = getUpdatedBoard(potentialMoves[i], preMoveBoard, userName) #only needs uN for castling considerations

        #everywhere the opponent could physically get to in this hypothetical board
        opponentPotentialMoves = getPotentialMoves(potentialBoard, getUserColor(getOtherUser(userName)), potentialMoves[i])

        #for each of those hypothetical opponent moves...
        for opponentMove in opponentPotentialMoves:
            if (opponentMove.endswith(getKingSquare(getUserColor(userName), potentialBoard))):
                if potentialMoves[i] in validMoves:
                    print("removing: " + str(potentialMoves[i]))
                    validMoves.remove(potentialMoves[i])
                break
    return validMoves


    #HERE'S WHAT STALEMATE IS
    #we are NOT in check in current board
    #all potential moves would bring us check

    #CHECKMATE
    #WE ARE in check in current board
    #all potential moves would keep us still in check
