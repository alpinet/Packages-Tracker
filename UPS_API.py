import requests
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import date
import time
import json
import ast
import USPS_API
import FedEx_API
from flask import Flask, render_template, escape, request, make_response, flash
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)


#1Z7R16180300026456 tracking number UPS
def get_json_dict(tracking_number_input):
    data = {
        "UPSSecurity": {
            "UsernameToken": {
                "Username": "alpinetang26",
                "Password": "lakerzRgood23601!"
            },
            "ServiceAccessToken": {
                "AccessLicenseNumber": "CD732771103FDC95"
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

#with open('usps.json', 'w') as outfile:
#    json.dump(get_json_dict("1ZRA15530376445450").json(), outfile, indent=4)

def current_city(tracking_number_input):
    return(get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["ActivityLocation"]["Address"][
              "City"])

def current_state(tracking_number_input):
    return(get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["ActivityLocation"]["Address"][
              "StateProvinceCode"])

def current_zipCode(tracking_number_input):
    return(get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["ActivityLocation"]["Address"][
              "PostalCode"])

def current_country(tracking_number_input):
    return(get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["ActivityLocation"]["Address"][
              "CountryCode"])

def current_status_description(tracking_number_input):
    return(get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["Status"]["Description"])

def current_date(tracking_number_input):
    date = (get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["Date"])
    return (date[4:6] + "/" + date[6:8] + "/" + date[0:4])
def current_time(tracking_number_input):
    time = (get_json_dict(tracking_number_input).json()["TrackResponse"]["Shipment"]["Package"]["Activity"][0]["Time"])
    if int(time[0:2]) >= 13:
        return (str(int(time[0:2]) - 13) + ":" + str(int(time[2:4])) + "PM")
    else:
        return (str(int(time[0:2])) + ":" + str(int(time[2:4])) + "AM")

def current_dateTime(tracking_number_input):
    return str(current_date(tracking_number_input)) + " at " + str(current_time(tracking_number_input))

def UPS_estimated_delivery_date(tracking_number_input):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome("/Users/josephtang/PycharmProjects/FirstSeleniumTest/drivers/chromedriver",
                              options=options)

    driver.get("https://www.ups.com/track?loc=en_US&tracknum=" + tracking_number_input + "&requester=MB/trackdetails")
    wait = WebDriverWait(driver, 10)
    men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="stApp_scheduledDeliveryDay"]')))
    #print(driver.find_elements_by_xpath('//*[@id="stApp_scheduledDeliveryDay"]'))
    delivery_date = driver.find_elements_by_xpath("//*[@id='stApp_scheduledDeliveryDay']")[0].text
    delivery_day = driver.find_elements_by_xpath("//*[@id='stApp_scheduledDelivery']")[0].text
    delivery_time = driver.find_elements_by_xpath("//*[@id='stApp_packageStatusTimeLbl_time']")[0].text
    return (str(delivery_date) + str(delivery_day) + str(delivery_time))

def UPS_list(trackingNum):
    company = "UPS"
    try:
        location = str(current_city(trackingNum)) + ", " + str(current_state(trackingNum)) + " " + str(
            current_zipCode(trackingNum))
    except:
        location = str(current_city(trackingNum)) + ", " + str(current_state(trackingNum))
    status = str(current_status_description(trackingNum))
    dateTime = str(current_date(trackingNum)) + " at " + str(current_time(trackingNum))
    if (status != "Delivered"):
        return [company, trackingNum, location, status, dateTime, UPS_estimated_delivery_date(trackingNum)]
    else:
        return [company, trackingNum, location, status, dateTime, "Completed at " + dateTime]

def USPS_list(trackingNum):
    company = "USPS"
    location = str(USPS_API.current_city(trackingNum)) + ", " + str(USPS_API.current_state(trackingNum)) + str(USPS_API.current_zipcode(trackingNum))
    status = USPS_API.current_status(trackingNum)
    dateTime = str(USPS_API.current_dateTime(trackingNum))
    return [company,trackingNum,location,status,dateTime]

def FedEx_list(trackingNum):
    return FedEx_API.setUpDriver(trackingNum)

def updateTableDict(aList, tableDict = {}):
    empty_dict = {}
    for item in aList:
        if len(item) == 18: #UPS
            try:
                if(current_dateTime(item) != tableDict[item][4]):
                    empty_dict[item] = UPS_list(item)
                else:
                    empty_dict[item] = tableDict[item]
            except:
                empty_dict[item] = UPS_list(item)
        if len(item) == 22: #USPS
            try:
                if(USPS_API.current_dateTime != tableDict[item][4]):
                    empty_dict[item] = USPS_list(item)
                else:
                    empty_dict[item] = tableDict[item]
            except:
                empty_dict[item] = USPS_list(item)
        if len(item) == 12: #FEDEX
            try:
                empty_dict[item] = FedEx_list(item,tableDict[item][3])
            except:
                empty_dict[item] = FedEx_list(item)
    return empty_dict

@app.route('/', methods = ['GET', 'POST'])
def home_page():
    today = date.today()
    if (int(time.strftime("%I:%M")[0:2]) > 12):
        current_time = str(time.strftime("%I:%M")) + "PM"
    else:
        current_time = (str(time.strftime("%I:%M")) + "AM")

    current_dateTime = today.strftime("%m/%d/%y") + " at " + current_time

    if request.method == 'POST':
        try:
            tableDict = updateTableDict(ast.literal_eval(request.cookies.get('table')))
            tableDictKeys = ast.literal_eval(request.cookies.get('table'))
        except:
            tableDict = {}
            tableDictKeys = []
        try:
            trackingNum = request.form['AddTrackingNum']
            if (len(request.form['AddTrackingNum']) == 18):
                tableDict[trackingNum] = UPS_list(trackingNum)
            elif (len(request.form['AddTrackingNum']) == 22):
                tableDict[trackingNum] = USPS_list(trackingNum)
            elif (len(request.form['AddTrackingNum']) == 12):
                tableDict[trackingNum] = FedEx_list(trackingNum)
            else:
                flash("Invalid Tracking Number; Must be UPS, USPS, or FedEx")
            tableDictKeys.append(trackingNum)

            resp = make_response(render_template('after.html', tableDict=tableDict, current_dateTime=current_dateTime))
            resp.set_cookie('table', str(tableDictKeys))
            return resp
        except:
            trackingNum = request.form['RemoveTrackingNum']
            del tableDict[trackingNum]
            tableDictKeys.remove(trackingNum)

            resp = make_response(render_template('after.html', tableDict=tableDict, current_dateTime=current_dateTime))
            resp.set_cookie('table', str(tableDictKeys))
            return resp
    else:
        if 'table' in request.cookies:
            return render_template('after.html',tableDict= updateTableDict(ast.literal_eval(request.cookies.get('table'))),current_dateTime=current_dateTime)
        else:
            return render_template('home.html', current_dateTime=current_dateTime)


if __name__ == "__main__":
    app.run(debug=True)