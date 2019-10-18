from uber_rides.session import Session
from uber_rides.client import UberRidesClient
import uber_rides.errors
import re
from geopy.geocoders import GoogleV3
from subprocess import call
#from phoneHome import user, pwd
user = "XXXXX"
pwd = "XXXXX"

session = Session(server_token="XXXXX")
client = UberRidesClient(session)

callPhrases = ["uber","ride"]

usageInstructions = ("Get a ride in the city.")

def generateResponse(tailSMS, adminStatus, userName, relationalEmail, driver):
    geolocator = GoogleV3(api_key="XXXXX", domain='maps.googleapis.com')
    if(tailSMS.startswith("price")):
        fromto = re.compile("price .+ to .+")
        if(re.match(fromto, tailSMS)):
            fromLocation = geolocator.geocode(getFrom(tailSMS))
            toLocation = geolocator.geocode(getTo(tailSMS))
            try:
                return(getEstimates(fromLocation, toLocation))
            except AttributeError:
                return("Location not found.")
            except uber_rides.errors.ClientError:
                return("Distance between locations exceeds 100 miles.")
        else:
            return("Improper input. \nProper format is:\n\'uber price <fromAddress> to <toAddress>\'")
    elif(tailSMS.startswith("request")):
        if(adminStatus == True):
            fromto = re.compile("request .+ to .+")
            if(re.match(fromto, tailSMS)):
                fromLocation = geolocator.geocode(getFrom(tailSMS))
                toLocation = geolocator.geocode(getTo(tailSMS))
                try:
                    #ensure locations exist and are in range by doing a price check
                    #not printing or storing this information, though
                    getEstimates(fromLocation, toLocation)
                except AttributeError:
                    return("Location not found.")
                except uber_rides.errors.ClientError:
                    return("Distance between locations exceeds 100 miles.")
                usersPhoneNumber = relationalEmail.split(".")[1]


                #TODO change to modules/submodules/ubsersub.py.....
                call(["python", "modules/submodules/ubersub.py", user, pwd, str(fromLocation.latitude), str(fromLocation.longitude), str(toLocation.latitude), str(toLocation.longitude), usersPhoneNumber], shell=True)
                return("Starting new Selenium Instance. Your ride request will be sent shortly.")
            else:
                return("Improper input. \nProper format is:\n\'uber request <fromAddress> to <toAddress>\'")
        else:
            return("You lack the proper admin credentials to request rides.")
    return("Improper input. \nProper format is:\n\'uber [price/request] <fromAddress> to <toAddress>\'")




def getEstimates(fromLocation, toLocation):
    response = client.get_price_estimates(start_latitude=fromLocation.latitude, start_longitude=fromLocation.longitude, end_latitude=toLocation.latitude, end_longitude=toLocation.longitude)

    estimates = response.json.get('prices')

    reply = ""

    for element in estimates:
        if(element.get('display_name') == 'UberX'):
            fromAddress = ""
            toAddress = ""

            justANumber = re.compile("\d+$")

            if(re.match(justANumber, fromLocation.address.split(",",1)[0])):
                fromAddress = fromLocation.address.split(",")[0] + fromLocation.address.split(",")[1]
            else:
                fromAddress = fromLocation.address.split(",")[0]

            if(re.match(justANumber, toLocation.address.split(",",1)[0])):
                fromAddress = toLocation.address.split(",")[0] + toLocation.address.split(",")[1]
            else:
                toAddress = toLocation.address.split(",")[0]

            miles = element.get('distance')
            minutes = element.get('duration')/60
            priceEstimate = element.get('estimate')

            reply = fromAddress + " to " + toAddress + "\n" + str(miles) + " miles\n" + str(minutes) + " minutes\n" + priceEstimate
            break

    return(reply)

def getFrom(tailSMS):
    splitSMS = tailSMS.split()
    i = 1 #to skip 'prices'
    fromString = ""
    while(splitSMS[i] != "to"):
        fromString += splitSMS[i] + " "
        i += 1
    return fromString

def getTo(tailSMS):
    splitSMS = tailSMS.split(" to ")
    toString = splitSMS[1]
    return toString

#print(generateResponse("price 700 E Mercer St. to Chuck's Hop Shop Central District", True, "hunna", "17076536037.12067341810.KgJLfz3rS2@txt.voice.google.com", 7))
