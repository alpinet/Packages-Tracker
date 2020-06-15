import requests
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

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
        return (str(int(time[0:2]) - 13) + ":" + str(int(time[2:5])) + "PM")
    else:
        return (str(int(time[0:2])) + ":" + str(int(time[2:5])) + "AM")

def current_dateTime(tracking_number_input):
    return str(current_date(tracking_number_input)) + " at " + str(current_time(tracking_number_input))

def UPS_estimated_delivery_date(tracking_number_input):
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome("/Users/josephtang/PycharmProjects/FirstSeleniumTest/drivers/chromedriver",options=options)

        driver.get("https://www.ups.com/track?loc=en_US&tracknum=" + tracking_number_input + "&requester=MB/trackdetails")
        wait = WebDriverWait(driver, 10)
        men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="stApp_scheduledDeliveryDay"]')))
        #print(driver.find_elements_by_xpath('//*[@id="stApp_scheduledDeliveryDay"]'))
        delivery_date = driver.find_elements_by_xpath("//*[@id='stApp_scheduledDeliveryDay']")[0].text
        delivery_day = driver.find_elements_by_xpath("//*[@id='stApp_scheduledDelivery']")[0].text
        delivery_time = driver.find_elements_by_xpath("//*[@id='stApp_packageStatusTimeLbl_time']")[0].text
        return (str(delivery_date) + str(delivery_day) + str(delivery_time))
    except:
        return "Completed delivery on ", current_dateTime(tracking_number_input)

start_time = time.time()
print(current_city("1ZRA15530376445450") + current_time("1ZRA15530376445450") + current_country("1ZRA15530376445450") + current_date("1ZRA15530376445450")
      + current_dateTime("1ZRA15530376445450") + current_state("1ZRA15530376445450") + current_status_description("1ZRA15530376445450") + current_zipCode("1ZRA15530376445450"))
print("--- %s seconds ---" % (time.time() - start_time))
