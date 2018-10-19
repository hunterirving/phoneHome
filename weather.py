#All valid phrases used to call this function
callPhrases = ["weather"]

#Server-wide default weather location
loc = "Seattle, WA"

#This string will be sent to users when they type "help <callPhrase>"
usageInstructions = ("Returns daily weather forecast for a given location." + "\nIf no location is specified, returns weather for " + loc + ".\nUsage: \"weather [location]\"")

#Server-wide default weather location
loc = "Seattle, WA"
from weather import Weather, Unit

def generateResponse(tailSMS, adminStatus, userName, relationalEmail, driver):
	global loc
	try:
		if (tailSMS != ""):
			loc = tailSMS
		w = Weather(unit=Unit.FAHRENHEIT)
		data = w.lookup_by_location(loc)
		forecasts = data.forecast
		first = forecasts[0]
		return data.location.city + "," + data.location.region + "\n"  + first.text + "\nTemp " + data.condition.temp + " F\nHigh " + first.high + " F\nLow " + first.low + " F\nWind " + data.wind.speed + " mph"
	except:
		return ("Invalid input to weather module. Reply \"help weather\" for usage instructions.")
