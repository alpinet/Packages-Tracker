from datetime import date, datetime
import time
import ast
import USPS_API
import FedEx_API
import UPS_API
from flask import Flask, render_template, request, make_response, flash
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)


def UPS_list(trackingNum):
    company = "UPS"
    try:
        location = str(UPS_API.current_city(trackingNum)) + ", " + str(UPS_API.current_state(trackingNum)) + " " + str(
            UPS_API.current_zipCode(trackingNum))
    except:
        location = str(UPS_API.current_city(trackingNum)) + ", " + str(UPS_API.current_state(trackingNum))
    status = str(UPS_API.current_status_description(trackingNum))
    dateTime = str(UPS_API.current_date(trackingNum)) + " at " + str(UPS_API.current_time(trackingNum))
    if (status != "Delivered"):
        return [company, trackingNum, location, status, dateTime, UPS_API.UPS_estimated_delivery_date(trackingNum),"" ]
    else:
        return [company, trackingNum, location, status, dateTime, "Completed on " + dateTime, ""]

def USPS_list(trackingNum):
    company = "USPS"
    location = str(USPS_API.current_city(trackingNum)) + ", " + str(USPS_API.current_state(trackingNum)) + " " + str(USPS_API.current_zipcode(trackingNum))
    status = USPS_API.current_status(trackingNum)
    dateTime = str(USPS_API.current_dateTime(trackingNum))
    expected = str(USPS_API.expected_delivery_date(trackingNum))
    if ("Delivered" in status):
        return [company, trackingNum, location, status, dateTime, "Completed on " + dateTime]
    else:
        return [company, trackingNum, location, status, dateTime, expected]

def FedEx_list(trackingNum):
    return FedEx_API.setUpDriver(trackingNum)

def updateTableDict(aList, tableDict = {}):
    empty_dict = {}
    for item in aList:
        if len(item) == 18: #UPS
            try:
                if(UPS_API.current_dateTime(item) != tableDict[item][4]):
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
                empty_dict[item] = FedEx_list(item)
            except:
                empty_dict[item] = FedEx_list(item)
    return empty_dict

@app.route('/', methods = ['GET', 'POST'])
def home_page():
    current_dateTime = datetime.now().strftime("%m/%d/%Y %I:%M:%p")
    try:
        tableDict = updateTableDict(ast.literal_eval(request.cookies.get('table')))
        print("3")
        tableDictKeys = ast.literal_eval(request.cookies.get('table'))
        print("4")
    except:
        tableDict = {}
        tableDictKeys = []
    if request.method == 'POST':
        if "AddTrackingNum" in request.form:
            trackingNum = request.form['AddTrackingNum']
            if (len(request.form['AddTrackingNum']) == 18):
                try:
                    tableDict[trackingNum] = UPS_list(trackingNum)
                except:
                    flash("Invalid UPS Tracking Number")
            elif (len(request.form['AddTrackingNum']) == 22):
                try:
                    tableDict[trackingNum] = USPS_list(trackingNum)
                except:
                    flash("Invalid USPS Tracking Number")
            elif (len(request.form['AddTrackingNum']) == 12):
                try:
                    tableDict[trackingNum] = FedEx_list(trackingNum)
                except:
                    flash("Invalid FedEx Tracking Number")
            else:
                flash("Invalid Tracking Number; Must be UPS, USPS, or FedEx")
            tableDictKeys.append(trackingNum)

            resp = make_response(render_template('after.html', tableDict=tableDict, current_dateTime=current_dateTime))
            resp.set_cookie('table', str(tableDictKeys))
            return resp
        elif "RemoveTrackingNum" in request.form:
            trackingNum = request.form['RemoveTrackingNum']
            print(trackingNum)
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
    app.run(debug=False)