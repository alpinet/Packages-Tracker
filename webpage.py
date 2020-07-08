from datetime import datetime
from pytz import timezone
import pytz
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


def UPS_list(trackingNum, itemLabel):
    status = (UPS_API.current_status_description(trackingNum))
    if status == False:
        raise ValueError("Too many requests. Please wait a little and try again.")
    else:
        status = str(status)
    company = "UPS"
    try:
        location = str(UPS_API.current_city(trackingNum)) + ", " + str(UPS_API.current_state(trackingNum)) + " " + str(
            UPS_API.current_zipCode(trackingNum))
    except:
        location = str(UPS_API.current_city(trackingNum)) + ", " + str(UPS_API.current_state(trackingNum))
    if location == ",  " or location == ",":
        if UPS_API.check_valid(trackingNum) == False:
            raise KeyError("Not valid tracking num")
        location = "In Transit"
    if str(UPS_API.current_date(trackingNum)) == "":
        dateTime = ""
    else:
        dateTime = str(UPS_API.current_date(trackingNum)) + " at " + str(UPS_API.current_time(trackingNum))
    if (status != "Delivered"):
        return [itemLabel, company, trackingNum, location, status, dateTime, UPS_API.UPS_estimated_delivery_date(trackingNum)]
    else:
        return [itemLabel, company, trackingNum, location, status, dateTime, "Completed on " + dateTime]

def USPS_list(trackingNum, itemLabel):
    USPS_list = USPS_API.get_info(trackingNum)
    USPS_list.append(USPS_API.expected_delivery_date(trackingNum, USPS_list[4]))
    USPS_list.insert(0, itemLabel)
    if ("Delivered" in USPS_list[3]):
        USPS_list[5] = str("Completed on ") + str(USPS_list[4])
        return USPS_list
    else:
        return USPS_list

def FedEx_list(trackingNum, itemLabel):
    FedEx_list = FedEx_API.setUpDriver(trackingNum)
    FedEx_list.insert(0, itemLabel)
    return FedEx_list

def updateTableDict(aDict):
    for item in aDict:
        print(item)
        itemLabel = aDict[item][0]
        if "Completed" not in aDict[item]:
            if len(item) == 18: #UPS
                try:
                    aDict[item] = UPS_list(item, itemLabel)
                except ValueError:
                    flash("Too many requests. Please wait a little and try again.")
            elif len(item) > 21: #USPS
                aDict[item] = USPS_list(item, itemLabel)
            elif len(item) >= 12 and len(item) < 21: #FEDEX
                aDict[item] = FedEx_list(item, itemLabel)
    return aDict


@app.route('/', methods = ['GET', 'POST'])
def home_page():
    try:
        tableDict = ast.literal_eval(request.cookies.get('table'))
    except:
        tableDict = {}
    try:
        current_dateTime = str(request.cookies.get('current_dateTime'))
    except:
        current_dateTime = "Not yet been updated"
    if request.method == 'POST':
        if "AddTrackingNum" in request.form:
            if request.form['AddTrackingNum'] != "" and request.form['itemLabel'] != "":
                trackingNum = request.form['AddTrackingNum']
                itemLabel = request.form['itemLabel']
                if trackingNum in tableDict:
                    flash("Tracking number already in the table.")
                elif (len(request.form['AddTrackingNum']) == 18):
                    try:
                        tableDict[trackingNum] = UPS_list(trackingNum, itemLabel)
                    except:
                        flash("Invalid UPS Tracking Number")
                elif (len(request.form['AddTrackingNum']) > 21):
                    try:
                        tableDict[trackingNum] = USPS_list(trackingNum, itemLabel)
                    except:
                        flash("Invalid USPS Tracking Number")
                elif len(request.form['AddTrackingNum']) >= 12 and len(request.form['AddTrackingNum']) < 21:
                    try:
                        tableDict[trackingNum] = FedEx_list(trackingNum, itemLabel)
                    except:
                        flash("Invalid FedEx Tracking Number")
            elif request.form['AddTrackingNum'] == "":
                    flash("Must input tracking number.")
            elif request.form['itemLabel'] == "":
                    flash("Must add item name/description")
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
        elif "update" in request.form:
            date_format = '%m/%d/%Y %H:%M %Z'
            date = datetime.now(tz=pytz.utc)
            date = date.astimezone(timezone('US/Pacific'))
            current_dateTime = date.strftime(date_format)
            resp = make_response(render_template('after.html', tableDict=updateTableDict(tableDict), current_dateTime=current_dateTime))
            resp.set_cookie('table', str(tableDict))
            resp.set_cookie('current_dateTime', str(current_dateTime))
            return resp
    else:
        if 'table' in request.cookies:
            return render_template('after.html',tableDict= ast.literal_eval(request.cookies.get('table')), current_dateTime=current_dateTime)
        else:
            return render_template('home.html', current_dateTime=current_dateTime)


if __name__ == "__main__":
    app.run(debug=True)