#All valid phrases used to call this function
callPhrases = ["tip"]

#This string will be sent to users when they type "help <callPhrase>"
usageInstructions = ("Returns tip value for a given bill."
	"\nUsage: tip <total bill> [tip percent]"
	"\nIf no percent is specified, returns 15%, 20%, and 25% tip values.")

def generateResponse(tailSMS, adminStatus, userName, relationalEmail, driver):
	try:
		if(tailSMS[0] == "$"):
			tailSMS = tailSMS[1:]
			while(tailSMS[0] == " "):
				tailSMS = tailSMS[1:]
		floatSMS = float(tailSMS)
		return ("Bill " + '${:,.2f}'.format(floatSMS) + "\n\n15% tip " + '${:,.2f}'.format(floatSMS*0.15) + "\n20% tip "
			+ '${:,.2f}'.format(floatSMS*0.20) + "\n25% tip " + '${:,.2f}'.format(floatSMS*0.25))
	except:
		return ("Invalid input to tip module. Reply \"help tip\" for usage instructions.")
