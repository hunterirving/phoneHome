#All valid phrases used to call this function
callPhrases = ["wiki","wikipedia","what is","what was","who is","who was"]

#This string will be sent to users when they type "help <callPhrase>"
usageInstructions = "Returns the first sentence of any Wikipedia page.\nUsage: wiki <pageName>"

import wikipedia
import re

#returns the first sentence of any wikipedia article
def generateResponse(tailSMS, adminStatus, userName, relationalEmail, driver):
    try:
        if(tailSMS == ""):
            return ("Invalid input to wiki module. Reply \"help wiki\" for usage instructions.")
        #Check if we erroneously stored a partial first sentence
        #"wiki say anything; "wiki 12 hour clock"; good output should end like "<gotcha>."
        gotchas = ("Ltd.", "Bros.", "Mr.","Mrs.", "Ms.", "Dr.", "Prof.", "Jr.", "Sr.", "Ph.D.", "...", "a.m.", "p.m.", "etc.", "&c.", "P.S.", "Q.E.D.", "R.I.P.", "!")
        sentCount = 1

        summary = wikipedia.summary(tailSMS, sentences=sentCount)

        while(summary.endswith(gotchas)):
            sentCount = sentCount + 1
            #print(summary)
            #print("GOTCHA")
            summary = wikipedia.summary(tailSMS, sentences=sentCount)

        #remove duplicate spaces ex: "wiki papaya"
        return " ".join(stripParens(summary).split())

    except wikipedia.exceptions.DisambiguationError as didYouMean:
        return str(didYouMean)
    except wikipedia.exceptions.PageError as pageEr:
        return str(pageEr).replace(" Try another id!","") #don't get cute


def stripParens(inputString):
    i = 0
    stack = []

    while i < len(inputString):
        if(inputString[i] == "("):
            stack.append(i)
        elif(inputString[i] == ")"):
            if(len(stack) != 0):
                j = stack[len(stack)-1]
                inputString = (inputString[:stack.pop()-1] + inputString[(i+1):])
                i = j - 2
        i = i + 1
    return inputString
