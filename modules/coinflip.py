#All valid phrases used to call this function
callPhrases = ["flip", "flip a coin", "flip coin", "coin flip", "coinflip", "flipcoin", "coin", "heads or tails", "headsortails"]

#This string will be sent to users when they type "help <callPhrase>"
usageInstructions = ("Settle any argument.\n\nUsage: \"flip coin\"")

def generateResponse(tailSMS, adminStatus, userName, relationalEmail, driver):
	import random
	responses = ["Heads!","Tails!"]

	return random.choice(responses)
