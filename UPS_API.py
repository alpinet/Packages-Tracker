import requests
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import json

def get_json_dict(tracking_number_input):
    data = {
        "UPSSecurity": {
            "UsernameToken": {
                "Username":os.environ.get('username')
,
                "Password": os.environ.get('password')

            },
            "ServiceAccessToken": {
                "AccessLicenseNumber": os.environ.get('access_num')
            }
        },
        "TrackRequest": {
            "Request": {
                "RequestOption": "1",
                "TransactionReference": {
                    "CustomerContext": "Your Test Case Summary Description"
                }
            },
            "InquiryNumber": tracking_number_input
        }
    }
    r = requests.post(url="https://wwwcie.ups.com/rest/Track", json=data)
    return r

with open('usps.json', 'w') as outfile:
   json.dump(get_json_dict("1ZRA15530376445450").json(), outfile, indent=4)

def check_valid(tracking_number_input):
    try:
        if get_json_dict(tracking_number_input).json()["TrackResponse"]["Response"]["ResponseStatus"]["Code"] == "1":
            return True
        if get_json_dict(tracking_number_input).json()["response"]["errors"][0]["code"] == "10429":
            return True
    except:
        return False


def current_city(tracking_number_input):
    try:
        return(get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["ActivityLocation"]["Address"][
                  "City"])
    except:
        return ("")
def current_state(tracking_number_input):
    try:
        return(get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["ActivityLocation"]["Address"][
                  "StateProvinceCode"])
    except:
        return ""
def current_zipCode(tracking_number_input):
    try:
        return(get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["ActivityLocation"]["Address"][
              "PostalCode"])
    except:
        return ""
def current_country(tracking_number_input):
    try:
        return(get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["ActivityLocation"]["Address"][
              "CountryCode"])
    except:
        return ""
def current_status_description(tracking_number_input):
    try:
        if get_json_dict(tracking_number_input).json()["response"]["errors"][0]["code"] == "10429":
            return False
    except:
        try:
            return (get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["Status"][
                "Description"])
        except:
            return "Order Process: Ready for UPS"
def current_date(tracking_number_input):
    try:
        date = (get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["Date"])
        return (date[4:6] + "/" + date[6:8] + "/" + date[0:4])
    except:
        return ""
def current_time(tracking_number_input):
    try:
        time = (get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["Time"])
        if int(time[0:2]) >= 13:
            return (str(int(time[0:2]) - 12) + ":" + str(time)[2:4] + "PM")
        else:
            return (str(int(time[0:2])) + ":" + str(int(time[2:4])) + "AM")
    except:
        return ""
def current_dateTime(tracking_number_input):
    return str(current_date(tracking_number_input)) + " at " + str(current_time(tracking_number_input))

def UPS_estimated_delivery_date(tracking_number_input):
    if current_status_description(tracking_number_input) == "Order Process: Ready for UPS":
        return "Delivery date will be updated when UPS receives item"
    try:
        #options = Options()
        #options.add_argument("--headless")
        #driver = webdriver.Chrome("/Users/josephtang/PycharmProjects/FirstSeleniumTest/drivers/chromedriver",
                                  #options=options)
        driver = webdriver.PhantomJS()

        driver.get("https://www.ups.com/track?loc=en_US&tracknum=" + tracking_number_input + "&requester=MB/trackdetails")
        wait = WebDriverWait(driver, 10)
        men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="stApp_scheduledDeliveryDay"]')))
        #print(driver.find_elements_by_xpath('//*[@id="stApp_scheduledDeliveryDay"]'))
        delivery_date = driver.find_elements_by_xpath("//*[@id='stApp_scheduledDeliveryDay']")[0].text
        print(str(delivery_date))
        delivery_day = driver.find_elements_by_xpath("//*[@id='stApp_scheduledDelivery']")[0].text
        print(str(delivery_day))
        delivery_time = driver.find_elements_by_xpath("//*[@id='stApp_eodDate']")[0].text
        print(str(delivery_time))
        return (str(delivery_date) + " " + str(delivery_day) +" " + str(delivery_time))
    except Exception as e:
        print(e)
        return str("Completed delivery on ") + str(current_dateTime(tracking_number_input))