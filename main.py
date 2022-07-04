from actions import chrome_driver, random_wait, scrap_restaurant_details, getproxy, calculate_new_longitude_latitude, \
    find_original_longitude_latitude, write_csv
from constant import GRAB_FOOD_URL


def launch_scrapper():
    driver = chrome_driver()
    driver.get(GRAB_FOOD_URL)
    original_latitude, original_longitude = find_original_longitude_latitude(driver)

    restaurant_details = scrap_restaurant_details(driver, original_latitude, original_longitude)
    write_csv(restaurant_details)

launch_scrapper()
