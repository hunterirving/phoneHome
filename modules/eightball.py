#All valid phrases used to call this function
callPhrases = ["8ball", "8-ball", "8 ball",
	"magic 8ball", "magic 8-ball", "magic 8 ball",
	"eightball", "eight-ball", "eight ball",
	"magic eightball", "magic eight-ball", "magic eight ball"]

#This string will be sent to users when they type "help <callPhrase>"
usageInstructions = ("Usage: \"8ball <question>\"\n\nAsk a question, shake lightly, and..?")

def generateResponse(tailSMS, adminStatus, userName, relationalEmail, driver):
	import random
	responses = ["IT IS CERTAIN",
		"IT IS DECIDEDLY SO",
		"WITHOUT A DOUBT",
		"YES DEFINITELY",
		"YOU MAY RELY ON IT",
		"AS I SEE IT, YES",
		"MOST LIKELY",
		"OUTLOOK GOOD",
		"YES",
		"SIGNS POINT TO YES",
		"REPLY HAZY. TRY AGAIN",
		"ASK AGAIN LATER",
		"BETTER NOT TELL YOU NOW",
		"CANNOT PREDICT NOW",
		"CONCENTRATE AND ASK AGAIN",
		"DON'T COUNT ON IT",
		"MY REPLY IS NO",
		"MY SOURCES SAY NO",
		"OUTLOOK NOT SO GOOD",
		"VERY DOUBTFUL"]

	return random.choice(responses)
