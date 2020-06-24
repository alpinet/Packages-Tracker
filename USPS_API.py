from usps import USPSApi
import json
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
usps = USPSApi(os.environ.get('USPS_num'))
#9200190246573223291412 crystals track
#9500126510460081342890 vivians track
#9374869903504598954074 michelle's track
#9449010205561009777268 caleb's track
#print(type(track.result))
#with open('usps.json', 'w') as outfile:
#    json.dump(track.result, outfile, indent=4)

def get_info(trackingNum):
    tracking_results = usps.track(trackingNum).result
    print(tracking_results)
    if (tracking_results["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventTime"]) == None:
           current_time = ""
    else:
        current_time = tracking_results["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventTime"]
    current_date = tracking_results["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventDate"]
    current_status = tracking_results["TrackResponse"]["TrackInfo"]["TrackSummary"]["Event"]
    if (tracking_results["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventCity"]) == None:
        current_city = "Last location: " + (usps.track(trackingNum).result["TrackResponse"]["TrackInfo"]["TrackDetail"][0]["EventCity"])
    else:
        current_city = tracking_results["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventCity"]
    if (tracking_results["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventState"]) == None:
        current_state = ""
    else:
        current_state = tracking_results["TrackResponse"]["TrackInfo"]["TrackDetail"][0]["EventState"]
    if (tracking_results["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventZIPCode"]) == None:
        current_zipcode = ""
    else:
       current_zipcode = tracking_results["TrackResponse"]["TrackInfo"]["TrackSummary"]["EventZIPCode"]
    if (current_time == ""):
        current_dateTime = current_date
    else:
        current_dateTime = str(current_date) + " at " + str(current_time)
    current_location = str(current_city) + ", " + str(current_state) + " " + str(current_zipcode)
    return ["USPS", trackingNum, current_location, current_status, current_dateTime]
'''

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

'''

def expected_delivery_date(trackingNum, current_dateTime, check = 0):
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome("/Users/josephtang/PycharmProjects/FirstSeleniumTest/drivers/chromedriver",
                                  options=options)
        driver.get("https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=" + trackingNum)
        wait = WebDriverWait(driver, 10)

        men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='tracked-numbers']/div/div/div/div/div[1]/div[1]/h2/span/span[1]/strong")))
        day = driver.find_element_by_xpath(("//*[@id='tracked-numbers']/div/div/div/div/div[1]/div[1]/h2/span/span[1]/strong")).text
        month_year = driver.find_element_by_xpath('//*[@id="tracked-numbers"]/div/div/div/div/div[1]/div[1]/h2/span/span[1]/span').text
        time = driver.find_element_by_xpath('//*[@id="tracked-numbers"]/div/div/div/div/div[1]/div[1]/h2/span/span[2]/span/strong').text
        month_year_list = month_year.split()

        return str(month_year_list[0]) + " " + str(day) + " " + str(month_year_list[1]) + " by " + str(time)
    except:
        return (str("Completed delivery on ") +  str(current_dateTime))

