from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pickle
import requests

cookies_file = "cookies.pkl"
count = 0
section = YOUR_SECTION_NUMBER
initial_setup = False
webhook_url = YOUR_WEBHOOK_URL
course_name = YOUR_COURSE_NAME

def save_cookies(driver, file_path):
    with open(file_path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, file_path):
    with open(file_path, "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def send_discord_notification(section):
    user_id = YOUR_USER_ID
    message = {
        "content": f"<@{user_id}> YOUR SECTION IS HERE!!!!!! Section {section} is now available!"
    }
    requests.post(webhook_url, json=message)

def send_discord_error():
    message = {
        "content": "The script has stopped running."
    }
    requests.post(webhook_url, json=message)

def send_discord_counter(count):
    message = {
        "content": f"Script counter: {count}"
    }
    requests.post(webhook_url, json=message)


service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://tamu.collegescheduler.com/terms/Spring%202025%20-%20College%20Station")


# Load cookies and refresh the page
try:
    load_cookies(driver, cookies_file)
    driver.refresh()  # Refresh to apply cookies
except FileNotFoundError:
    print("Cookies file not found. Please log in and save cookies manually.")
    input("Press Enter after logging in and completing 2FA to save cookies...")
    save_cookies(driver, cookies_file)

# Loop to reload the page every 10 mins
try:
    while True:
        if not initial_setup:
            #Spring 2025 - College Station button
            button = driver.find_element(By.ID, "Spring 2025 - College Station")
            button.click()
            #Save and Continue button
            button = driver.find_element(By.CLASS_NAME, "css-elue75-hoverStyles-hoverStyles-defaultStyle-centerBlockCss")
            button.click()
            #Opening Sections for 314
            time.sleep(5)
            button = driver.find_element(By.CSS_SELECTOR, f"[aria-label='Sections for {course_name}']")
            button.click()
            initial_setup = True
        #Gathering 314 section numbers
        time.sleep(2)
        temp = driver.find_elements(By.CLASS_NAME, 'css-1p12g40-cellCss-hideOnMobileCss')
        sections_available = []
        all_spans = []
        for td in temp:
            spans = td.find_elements(By.TAG_NAME, "span")
            for span in spans:
                all_spans.append(span.text)
        for i in range(len(all_spans)):
            if len(all_spans[i]) == 5:
                sections_available.append(all_spans[i+1])
        print(sections_available)
        if str(section) in sections_available: #if the section is availabe - put discord stuff in here later
            print('YOUR SECTION IS HERE!!!!!!')
            send_discord_notification(section)
            break
        count += 1  # update counter
        send_discord_counter(count)
        time.sleep(600)  # Wait 10 minutes for less requests
        driver.refresh()
        print("Page reloaded")
except KeyboardInterrupt:
    print("Script stopped by user.")
finally:
    print(f"The script ran {count} times")
    send_discord_error()
    driver.quit()

