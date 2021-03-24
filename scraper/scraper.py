import calendar
import os
import platform
import sys
import urllib.request
import yaml
import traceback
import time
import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

# from langdetect import detect, detect_langs


# -------------------------------------------------------------
# -------------------------------------------------------------

# Global Variables


options = webdriver.ChromeOptions()

#  Code to disable notifications pop up of Chrome Browser
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--mute-audio")
options.add_argument("--no-sandbox")
options.add_argument("--headless")


total_scrolls = 3
current_scrolls = 0
scroll_time = 10

old_height = 0

insta_website_url = "https://www.instagram.com/accounts/login/"

CHROMEDRIVER_BINARIES_FOLDER = "bin"


data = []




# -------------------------------------------------------------
# -------------------------------------------------------------


def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 


def check_height(driver):
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height


# helper function: used to scroll the page
def scroll_and_scrap(tag, driver):
    done_posts = []

    global old_height, data
    current_scrolls = 0

    while True:
        try:
            aps1 = driver.find_elements_by_class_name('v1Nh3')
            aps2 = driver.find_elements_by_class_name('kIKUG')
            all_posts = intersection(aps1, aps2)

            for post in all_posts:
                if post not in done_posts:
                    try:
                        time.sleep(np.random.randint(1, 3))
                        post.click()
                        time.sleep(np.random.randint(3, 5))
                        txt = str(driver.find_element_by_class_name('C4VMK').text)
                        print(txt)
                        data.append((tag, txt))
                        driver.find_element_by_xpath('/html/body/div[5]/div[3]/button').click()
                        time.sleep(np.random.randint(1, 3))
                        done_posts.append(post)
                        print(len(done_posts))

                    except Exception as ex:
                        driver.refresh()
                        print(ex)

            if current_scrolls == total_scrolls:
                print(current_scrolls)
                return

            old_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, scroll_time, 0.05).until(
                lambda driver: check_height(driver)
            )
            current_scrolls += 1

        except TimeoutException:
            #print(traceback.format_exc())
            break
    return


# -------------------------------------------------------------
# -------------------------------------------------------------


def search_tag(tag, driver):
    try:
        tag = '#'+str(tag)
        time.sleep(np.random.randint(5, 7))
        search_field = driver.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div[2]/input')
        search_field.send_keys(tag)
        time.sleep(np.random.randint(1, 3))
        search_button = driver.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div[2]/div[3]/div/div[2]/div')
        search_button = search_button.find_elements_by_xpath('./*')[0]
        search_button = search_button.find_element_by_xpath('./a')
        print(search_button.text)
        search_button.click()
        time.sleep(np.random.randint(3, 6))
        return True
    except Exception as ex:
        print(ex)
    return False


# -------------------------------------------------------------
# -------------------------------------------------------------


def login(email, password, driver):
    """ Logging into our own profile """

    global insta_website_url

    time.sleep(np.random.randint(3, 6))

    try:

        driver.get(insta_website_url)
        driver.maximize_window()
        time.sleep(np.random.randint(3, 6))
        try:
            driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/button[1]').click()
            time.sleep(np.random.randint(3, 5))
        except Exception as ex:
            print(ex)

        
        # filling the form
        driver.find_element_by_name("username").send_keys(email)
        driver.find_element_by_name("password").send_keys(password)
        driver.find_element_by_id("loginForm").find_elements_by_tag_name('button')[1].click()
        time.sleep(np.random.randint(2, 4))
        driver.find_elements_by_tag_name('button')[0].click()

    except Exception as ex:
        print(ex,traceback.format_exc())
        print("There's some error in log in.")
        print(sys.exc_info()[0])
        exit(1)


def get_driver():
    try:
        platform_ = platform.system().lower()
        chromedriver_versions = {
            "linux": os.path.join(
                os.getcwd(), CHROMEDRIVER_BINARIES_FOLDER, "chromedriver_linux64",
            ),
            "darwin": os.path.join(
                os.getcwd(), CHROMEDRIVER_BINARIES_FOLDER, "chromedriver_mac64",
            ),
            "windows": os.path.join(
                os.getcwd(), CHROMEDRIVER_BINARIES_FOLDER, "chromedriver_win32.exe",
            ),
        }

        driver = webdriver.Chrome(
            executable_path=chromedriver_versions[platform_], options=options
        )

        return driver
    except Exception as ex:
        # print(ex,traceback.format_exc())
        print(
            "Kindly replace the Chrome Web Driver with the latest one from "
            "http://chromedriver.chromium.org/downloads "
            "and also make sure you have the latest Chrome Browser version."
            "\nYour OS: {}".format(platform_)
        )
        exit(1)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


def scrapper(tags, **kwargs):

    global data

    i,j = 0,0

    with open('creds_validator.txt', 'r') as fl:
        a = int(fl.read())
    if a == 1:
        i,j = 1,2
    elif a == 2:
        j,i = 1,2


    if tags:

        with open("instagram_credentials"+str(i)+".yaml", "r") as ymlfile:
            cfg = yaml.safe_load(stream=ymlfile)

        if ("password" not in cfg) or ("email" not in cfg):
            print("Your email or password is missing. Kindly write them in credentials.txt")
            exit(1)

        print("\nStarting Scraping...")

        with get_driver() as driver: 
            print(driver)

            login(cfg["email"], cfg["password"], driver)
            print('\nLogin Successfull\n')

            time.sleep(np.random.randint(4, 6))

            if driver.current_url == insta_website_url:
                with open("instagram_credentials"+str(j)+".yaml", "r") as ymlfile:
                    cfg = yaml.safe_load(stream=ymlfile)
                login(cfg["email"], cfg["password"], driver)
                print('\nLogin Successfull\n')

            with open('creds_validator.txt', 'w') as fl:
                if i == 1:
                    fl.write('2')
                elif i == 2:
                    fl.write('1')
                else:
                    exit(1)
            
            time.sleep(np.random.randint(4, 6))

            if driver.current_url == insta_website_url:
                print('something wrong with credentials !!!')
                exit(1)

            for key, values in tags.items():
                try:
                    os.mkdir("data/"+key)
                except Exception as ex:
                    print(ex)
                for tag in values:

                    if search_tag(tag, driver):
                        pass
                    else:
                        search_tag(tag, driver)

                    print('\nSearched Successfull\n')

                    time.sleep(np.random.randint(2, 4))
                    scroll_and_scrap(tag, driver)
                    time.sleep(np.random.randint(2, 4))

                    print('\nScraped Successfull\n')

                    print(len(data),data)

                    df = pd.DataFrame(data)
                    df.to_csv('data/'+key+'/'+tag+'.csv')

                    time.sleep(np.random.randint(1, 2))

                    driver.get("https://www.instagram.com/")
                    data=[]

    else:
        print("No tag given")


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
