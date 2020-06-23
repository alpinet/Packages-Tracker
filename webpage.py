from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import ast
import USPS_API
import FedEx_API
import UPS_API
from flask import Flask, render_template, request, make_response, flash
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)

def create_driver():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome("/Users/josephtang/PycharmProjects/FirstSeleniumTest/drivers/chromedriver", options=options)
    return driver

def UPS_list(trackingNum, driver):
    company = "UPS"
    try:
        location = str(UPS_API.current_city(trackingNum)) + ", " + str(UPS_API.current_state(trackingNum)) + " " + str(
            UPS_API.current_zipCode(trackingNum))
    except:
        location = str(UPS_API.current_city(trackingNum)) + ", " + str(UPS_API.current_state(trackingNum))
    status = str(UPS_API.current_status_description(trackingNum))
    dateTime = str(UPS_API.current_date(trackingNum)) + " at " + str(UPS_API.current_time(trackingNum))
    if (status != "Delivered"):
        return [company, trackingNum, location, status, dateTime, UPS_API.UPS_estimated_delivery_date(trackingNum, driver),"" ]
    else:
        return [company, trackingNum, location, status, dateTime, "Completed on " + dateTime, ""]

def USPS_list(trackingNum, driver):
    company = "USPS"
    location = str(USPS_API.current_city(trackingNum)) + ", " + str(USPS_API.current_state(trackingNum)) + " " + str(USPS_API.current_zipcode(trackingNum))
    status = USPS_API.current_status(trackingNum)
    dateTime = str(USPS_API.current_dateTime(trackingNum))
    expected = str(USPS_API.expected_delivery_date(trackingNum, driver))
    if ("Delivered" in status):
        return [company, trackingNum, location, status, dateTime, "Completed on " + dateTime, ""]
    else:
        return [company, trackingNum, location, status, dateTime, expected, ""]

def FedEx_list(trackingNum, driver):
    return FedEx_API.setUpDriver(trackingNum, driver)

def updateTableDict(aDict, tableDict = {}):
    print(str(aDict))
    for item in aDict:
        if "Completed" not in aDict[item]:
            if len(item) == 18: #UPS
                aDict[item] = UPS_list(item)
            if len(item) == 22: #USPS
                aDict[item] = USPS_list(item)
            if len(item) == 12: #FEDEX
                aDict[item] = FedEx_list(item)
    return aDict

@app.route('/', methods = ['GET', 'POST'])
def home_page():
    print("1")
    local_time = str(datetime.now(timezone.utc).astimezone())
    current_date = str(local_time[5:7]) + "/" + str(local_time[8:10]) + "/" + str(local_time[0:4])
    if int(local_time[11:13]) > 12:
        current_time = str(int(local_time[11:13]) - 12) + ":" + str(local_time[14:16]) + " PM"
    else:
        current_time = str(int(local_time[11:13])) + ":" + str(local_time[14:16]) + " AM"
    current_dateTime = current_date + " " + current_time
    print("2")
    try:
        tableDict = updateTableDict(ast.literal_eval(request.cookies.get('table')))
    except:
        tableDict = {}
    print("3")
    if request.method == 'POST':
        if "AddTrackingNum" in request.form:
            driver = create_driver()
            trackingNum = request.form['AddTrackingNum']
            if trackingNum in tableDict:
                flash("Tracking number already in the table.")
            elif (len(request.form['AddTrackingNum']) == 18):
                try:
                    tableDict[trackingNum] = UPS_list(trackingNum, driver)
                except:
                    flash("Invalid UPS Tracking Number")
            elif (len(request.form['AddTrackingNum']) == 22):
                try:
                    tableDict[trackingNum] = USPS_list(trackingNum,driver)
                except:
                    flash("Invalid USPS Tracking Number")
            elif (len(request.form['AddTrackingNum']) == 12):
                try:
                    tableDict[trackingNum] = FedEx_list(trackingNum, driver)
                except:
                    flash("Invalid FedEx Tracking Number")
            else:
                flash("Invalid Tracking Number; Must be UPS, USPS, or FedEx")
            resp = make_response(render_template('after.html', tableDict=tableDict, current_dateTime=current_dateTime))
            resp.set_cookie('table', str(tableDict))
            return resp
        elif "RemoveTrackingNum" in request.form:
            trackingNum = request.form['RemoveTrackingNum']
            del tableDict[trackingNum]
            resp = make_response(render_template('after.html', tableDict=tableDict, current_dateTime=current_dateTime))
            resp.set_cookie('table', str(tableDict))
            return resp
    else:
        if 'table' in request.cookies:
            return render_template('after.html',tableDict= updateTableDict(ast.literal_eval(request.cookies.get('table'))),current_dateTime=current_dateTime)
        else:
            return render_template('home.html', current_dateTime=current_dateTime)


if __name__ == "__main__":
    app.run(debug=False)