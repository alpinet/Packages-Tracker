from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import date
import time

#391425387258

def setUpDriver(trackingNum, check = 0):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome("/Users/josephtang/PycharmProjects/FirstSeleniumTest/drivers/chromedriver", options=options)
    driver.get("https://www.fedex.com/apps/fedextrack/index.html?tracknumbers=" + trackingNum + "&cntry_code=us")
    wait = WebDriverWait(driver, 10)
    men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='container']/div/div/div[2]/div/div[1]/div[2]/div[3]/div/div[3]/div/div[1]/div/div[2]/div[5]/div/h3[3]")))
    current_status1 = driver.find_elements_by_xpath("//*[@id='container']/div/div/div[2]/div/div[1]/div[2]/div[3]/div/div[3]/div/div[1]/div/div[2]/div[5]/div/h3[1]")[0].text
    current_status2 = driver.find_elements_by_xpath("//*[@id='container']/div/div/div[2]/div/div[1]/div[2]/div[3]/div/div[3]/div/div[1]/div/div[2]/div[5]/div/h3[2]")[0].text
    current_status = current_status1 + ", " + current_status2
    if current_status == check:
        return
    #CURRENT LOCATION
    if current_status1 == "DELIVERED":
        current_location = driver.find_elements_by_xpath("//*[@id='container']/div/div/div[2]/div/div[1]/div[2]/div[3]/div/div[3]/div/div[1]/div/div[6]/div[2]/div/p[6]")[0].text
    else:
        current_location = driver.find_elements_by_xpath("//*[@id='container']/div/div/div[2]/div/div[1]/div[2]/div[3]/div/div[3]/div/div[1]/div/div[2]/div[5]/div/h3[3]")[0].text
    #CURRENT STATUS
    #CURRENT DATE/TIME
    today = date.today()
    if (int(time.strftime("%I:%M")[0:2]) > 12):
        current_time = str(time.strftime("%I:%M")) + "PM"
    else:
        current_time = (str(time.strftime("%I:%M")) + "AM")

    current_dateTime = today.strftime("%m/%d/%y") + " at " + current_time
    if "DELIVERED" in current_status:
        delivery_date = "Completed on " + str(driver.find_elements_by_xpath("//*[@id='container']/div/div/div[2]/div/div[1]/div[2]/div[3]/div/div[3]/div/div[1]/div/div[2]/h1/div[2]")[0].text)
    else:
        delivery_date = str(driver.find_elements_by_xpath("//*[@id='container']/div/div/div[2]/div/div[1]/div[2]/div[3]/div/div[3]/div/div[1]/div/div[2]/h1/div[2]")[0].text)
    return ["FedEx", trackingNum, current_location, current_status, current_dateTime,delivery_date]



