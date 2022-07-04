import random
import time
import csv
import requests
import math
from bs4 import BeautifulSoup
from selenium import webdriver

from constant import CLASS_NAME, EARTH, DEFAULT_LATITUDE, DEFAULT_LONGITUDE, header, PROXY_SITE_URL, PROXY_HEADER, \
    PROXY_LIST_CLASS_NAME, binary_location, driver_location


def getproxy():
    res = requests.get(PROXY_SITE_URL, PROXY_HEADER)
    soup = BeautifulSoup(res.text, "lxml")
    proxy_list = []
    for items in soup.select(PROXY_LIST_CLASS_NAME):
        proxy = ':'.join([item.text for item in items.select("td")[:2]])
        proxy_list.append(proxy)
    return proxy_list


def chrome_driver():
    proxy_list = getproxy()
    PROXY = random.choice(proxy_list)

    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s' % PROXY)
    # options.add_argument("--headless")
    options.binary_location = binary_location
    web_driver = webdriver.Chrome(executable_path=driver_location, chrome_options=options)
    web_driver.maximize_window()
    web_driver.implicitly_wait(10)

    return web_driver


def random_wait(a, b):
    t = random.randint(a, b)
    time.sleep(t)


def scrap_restaurant_details(driver, latitude, longitude):

    # load more button
    for i in range(5):
        driver.find_element_by_class_name(CLASS_NAME['load_more_button']).click()
        random_wait(5, 10)

    restaurant_list = driver.find_elements_by_class_name(CLASS_NAME['restaurant_list'])

    restaurant_master_list = []

    for restaurant in restaurant_list:
        restaurant_name = restaurant.find_element_by_class_name(CLASS_NAME['restaurant_name'])
        distance_time = restaurant.find_elements_by_class_name(CLASS_NAME['distance_time'])
        distance_time_text = distance_time[-1].text
        distance_time_text_list = distance_time_text.split(' ')
        if distance_time_text_list[-1] == 'km':
            distance = float(distance_time_text_list[-2]) * 1000
        else:
            distance = float(distance_time_text_list[-2])

        res_latitude, res_longitude = calculate_new_longitude_latitude(latitude, longitude, distance)
        restaurant_master_list.append([restaurant_name.text, distance, res_latitude, res_longitude])

    return restaurant_master_list


def calculate_new_longitude_latitude(latitude, longitude, distance):

    pi_value = math.pi

    m = (1 / ((2 * pi_value / 360) * EARTH)) / 1000
    new_latitude = latitude + (distance * m)

    cos = math.cos
    m = (1 / ((2 * math.pi / 360) * EARTH)) / 1000
    new_longitude = longitude + (distance * m) / cos(latitude * (math.pi / 180))

    return new_latitude, new_longitude


def find_original_longitude_latitude(driver):
    latitude, longitude = DEFAULT_LATITUDE, DEFAULT_LONGITUDE
    for cookie in driver.get_cookies():

        if cookie['name'] == 'location':

            value = cookie['value']
            longitude_text_index = value.index('longitude')
            latitude_text_index = value.index('latitude')
            address_text_index = value.index('address')
            latitude = value[latitude_text_index:longitude_text_index].replace('latitude%22%3A', '').replace('%2C%22',
                                                                                                             '')
            longitude = value[longitude_text_index:address_text_index].replace('longitude%22%3A', '').replace('%2C%22',
                                                                                                              '')

        return float(latitude), float(longitude)


def write_csv(data):

    with open('restaurant.csv', 'w', encoding='UTF8') as f:

        # create the csv writer
        writer = csv.writer(f)
        writer.writerow(header)

        # write rows to the csv file
        writer.writerows(data)
