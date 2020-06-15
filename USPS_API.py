from usps import USPSApi
import json
import sys
print(sys.version)
usps = USPSApi('025PERSO3705')
track = usps.track("9449010205561009777268")
#9200190246573223291412 crystals track
#9500126510460081342890 vivians track
#9374869903504598954074 michelle's track
#9449010205561009777268 caleb's track
#print(type(track.result))
with open('usps.json', 'w') as outfile:
    json.dump(track.result, outfile, indent=4)
def current_time(trackingNum):
    if (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventTime"]) == None:
           return ""
    return (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventTime"])

def current_date(trackingNum):
    return (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventDate"])

def current_status(trackingNum):
    return (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackSummary"]["Event"])

def current_city(trackingNum):
    if (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventCity"]) == None:
        return "Last location: " + (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackDetail"][0]["EventCity"])
    return (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventCity"])

def current_state(trackingNum):
    if (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventState"]) == None:
        return ""
    return (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackDetail"][0]["EventState"])

def current_zipcode(trackingNum):
    if (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventZIPCode"]) == None:
        return ""
    return (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventZIPCode"])

def current_dateTime(trackingNum):
    if (current_time(trackingNum) == ""):
        return current_date(trackingNum)
    else:
        return str(current_date(trackingNum)) + " at " + str(current_time(trackingNum))

print(current_status("9449010205561009777268"))
