import imaplib					#for accessing emails
#import wikipedia				#for searching wikipedia (pip install wikipedia)
import getpass					#hides characters as you type your password
#from weather import Weather, Unit #for pulling weather data (pip install weather-api)
import time                     #time.sleep(seconds) so we aren't flooding google's servers with requests

from selenium import webdriver #for interfacing directly with webpages (pip install selenium)
from selenium.webdriver.common.keys import Keys #import keyboard key press functionality

#for importing modules from "./modules"
import os, sys

#import seperate users.py file containing a list of whitelisted users
import users

#set default mailbox as INBOX
box = 'INBOX'
#initialize email server
imapserver = imaplib.IMAP4_SSL("imap.gmail.com", 993)

#these are populated at runtime
user = ""
pwd = ""
moduleNames = []

def importModules():
    requiredAttributes = [["callPhrases", "list"],["usageInstructions", "str"],["generateResponse", "function"]]
    print("Scanning for modules...")
    for file in os.listdir("./modules"):
        if file.endswith(".py"):
            moduleName = (file[:-3])
            print("Found " + moduleName + " module...")

            try:
                exec("import modules.{0} as {0}".format(moduleName), globals())
                for i in range(0, len(requiredAttributes)):
                    if(requiredAttributes[i][0] in eval("dir({0})".format(moduleName))):
                        if(eval("str(type({}.{}))".format(moduleName,requiredAttributes[i][0])).split("\'")[1] == requiredAttributes[i][1]):
                            pass
                        else:
                            #Type Error in MODULENAME: Expected requiredAttribute to be of type TYPE; Found type TYPE
                            print("Type error in " + moduleName + ": Expected " + requiredAttributes[i][0] + " to be of type \""
                                + requiredAttributes[i][1] + "\"; Found type \"" + eval("str(type({}.{}))".format(moduleName,requiredAttributes[i][0])).split("\'")[1] + "\"")
                            raise ImportError
                    else:
                        print("Missing required attribute \'" + requiredAttributes[i][0] + "\' in " + moduleName + " module.")
                        raise ImportError
                moduleNames.append(moduleName)
                print("Successfully imported " + moduleName + " module.")
            except ImportError:
                print("Failed to import " + moduleName + " module.")
                exec("del globals()[\'{0}\']".format(moduleName))
                print("Fix error in " + moduleName + ".py or remove " + moduleName + ".py from modules directory to continue initialization.")
                quit()

#get user's login information from command line
def setLoginCredentials():
    global user, pwd

    for x in range(0, 3):
        try:
            user = input("\nInput username for Google account: ")
            pwd = getpass.getpass("Input password for Google account: ")
            imapserver.login(user, pwd)
            imapserver.select(box)
            print("Successfully logged in as " + user + ".")
            break
        except Exception:
            print ("Login failed!")
            print ("Login attempts remaining: " + str(2-x))
            if(2-x == 0):
                quit()


#this function logs out/into mail server to avoid timeouts
def refreshServer(user, pwd):
    try:
        global imapserver, smtpserver
        imapserver.close()
        imapserver.logout()
        imapserver = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        imapserver.login(user, pwd)
        imapserver.select(box)
    except:
        print("Failed to connect to server.")

#this function is called after login credentials have been set
#opens new Firefox window and plugs directly into Google Voice
def initializeSelenium(user, pwd):
    #type username and click next
    driver.get("https://accounts.google.com/signin")

    driver.find_element_by_id("identifierId").send_keys(user)
    driver.find_element_by_id("identifierNext").click()
    #give it a second for password page to load in, then..

    try:
        time.sleep(1)
        driver.find_element_by_name("password").send_keys(pwd)
        element = driver.find_element_by_id('passwordNext')
        driver.execute_script("arguments[0].click();", element)
    except:
        #we gotta wait a little longer... hey, that's okay
        #we aren't in any rush right now
        time.sleep(1)
        driver.find_element_by_name("password").send_keys(pwd)
        element = driver.find_element_by_id('passwordNext')
        driver.execute_script("arguments[0].click();", element)

    #give Firefox 2 seconds to process the password we just typed in
    time.sleep(2)
    #Now that we've logged in, navigate to Google Voice page
    #whole program will hang here until page fires onLoad event
    driver.get("https://voice.google.com/messages")

#finds new messages in inbox, determines their raw SMS content,
#then calls parseSMS to determine how to handle the user's query
def checkMessages():
    for i in range(len(users.users)):
        #Do we have new messages from user at [i] ?
        status, response = imapserver.search(None, '(FROM "' + users.users[i][0] + '" UNSEEN)')

        #store e_ids for messages matching our criteria
        unread_msg_ids = response[0].split()
        print(str(len(unread_msg_ids)) + " new message(s) from user \"" + users.users[i][1] + "\": ")

        #build up an array containing raw email text of new messages from selected user
        #also, mark them as read
        raw_email = []
        for e_id in unread_msg_ids:
            status, response = imapserver.fetch(e_id, 'BODY.PEEK[TEXT]')
            raw_email.append(response[0][1])
            imapserver.store(e_id, '+FLAGS', '\Seen')

        for element in raw_email:
            rawSMS = rawEmailToRawSMS(element.decode("utf-8"))
            print("\n" + users.users[i][1] +"\'s message:\n\"" + rawSMS + "\"")

            #to determine what response to send, we only need
            #to know the original SMS body and that user's Admin Status
            response = parseSMS(rawSMS, users.users[i][2], users.users[i][1], users.users[i][0])

            #now that we have built our response, send it
            sendResponse(users.users[i][0].split(".")[1], response, driver)
            print("pH's response:\n\"" + response + "\"\n")

#Rip out Google's fancy Google Voice fluff
#Returns only the raw SMS text message that the user sent
def rawEmailToRawSMS(rawEmail):
    try:
        head ="<https://voice.google.com>\r\n"
        optionalInsert = "\r\nTo respond to this text message, reply to this email or visit Google Voice."
        tailStart = "\r\nYOUR ACCOUNT" #followed by more stuff.....
        rawSMS = " "

        #lop off head
        rawEmail = rawEmail.split(head)[1]
        #lop off insert (if it exists)
        rawEmail = rawEmail.replace(optionalInsert, "")

        #if: users message was more than just an empty string (or just spaces or newlines)...
        if(not(len(rawEmail.split(tailStart)) == 1)):
            rawSMS = rawEmail.split(tailStart)[0]

        return rawSMS

    except:
        #They tried to slip us up with some exotic characters
        #What was that, an emoji?
        return("Character Encoding Error :^(")

#Given a complete, raw SMS message recieved from the user,
#Call the appropriate submethod, which will return a response
#to parseSMS that parseSMS will then also return up to checkMessages
def parseSMS(rawSMS, adminStatus, userName, relationalEmail):
    lowSMS = rawSMS.lower()

    for i in range(0, len(moduleNames)):
        for j in range(0, eval("len({0}.callPhrases)".format(moduleNames[i]))):
            if(lowSMS.startswith(eval("{0}.callPhrases[j]".format(moduleNames[i])))):
                tailSMS = lowSMS[(len(eval("{0}.callPhrases[j]".format(moduleNames[i])))):]
                if(tailSMS != ""):
                #strip spaces between callPhrase and param(s)
                #assuming good input (ex they said "wiki    nintendo")
                    if(tailSMS[0] == " "):
                        while(tailSMS[0] == " "):
                            tailSMS = tailSMS[1:]
                            #now tailSMS contains only params
                    else:
                        continue #with for loop incrementing over callPhrases
                return truncateTo160(eval("{0}.generateResponse(tailSMS, adminStatus, userName, relationalEmail, driver)".format(moduleNames[i])))
    return commandNotFound(lowSMS)

def commandNotFound(com):
    if((len("Command \"" + com + "\" not recognized. Reply \"help\" for a list of available commands.") <= 160) and com != " "):
        return("Command \"" + com + "\" not recognized. Reply \"help\" for a list of available commands.")
    else:
        return("Command not found. Reply \"help\" for a list of available commands.")

#Uses Selenium to...
#1. Feed Google Voice sender's phone number and press Return to confirm
#2. Feed Google Voice the response to the sender's query and press Return to send
def sendResponse(usersPhoneNumber, responseString, driver):
    #split() up fake email to get just the true phone number, use that to send.
    #usersPhoneNumber = usersFakeEmail.split(".")[1]

    sendAMessageButton = driver.find_element_by_xpath("//div[@aria-label='Send a message']")
    driver.execute_script("arguments[0].click();", sendAMessageButton)

    #seems to be neccesary, give Firefox time to pop in text input field
    time.sleep(0.5)

    #find the "To:" field and type in the phone number we want to send to
    toField = driver.find_element_by_xpath("//input[@placeholder='Type a name or phone number']")
    toField.clear()
    toField.send_keys(usersPhoneNumber, Keys.RETURN)

    #Find message typing box, type message, hit return
    typeAMessageField = driver.find_element_by_xpath("//textarea[@aria-label='Type a message']")
    typeAMessageField.clear()
    typeAMessageField.send_keys(responseString, Keys.RETURN)

    #hang out for a sec while this sends.. is this neccesary?
    #time.sleep(1)

#if inputString is over 160 characters, truncates to 157 characters, then adds "..."
def truncateTo160(inputString):
    if(len(inputString) > 160):
        inputString = (inputString[:157] + "...")
    return inputString

def mainLoop():
    while(True):
        print("Refreshing servers...")
        refreshServer(user, pwd)
        print("Checking for new messages...")
        #check for new messages and reply to them if they exist
        checkMessages()
        for x in range(0, 5):
            print("Checking for new messages in " + box + " in 0." + str(5 - x) + " second(s)...", end = "\r")
            time.sleep(0.1)
        print("Checking for new messages in " + box + " in 0.0 second(s)...")

if __name__ == "__main__":
    importModules()
    setLoginCredentials()
    print("Starting Firefox using Gecko WebDriver...")
    driver = webdriver.Firefox()
    initializeSelenium(user, pwd)
    mainLoop()
