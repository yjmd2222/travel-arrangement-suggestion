from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent import futures
from datetime import datetime, timedelta

from crawling_rentcar import rentcar_crawl, get_date_combinations

s_date = datetime.today() + timedelta(days=1)
date_combos = get_date_combinations(s_date)
s_time_h_range = list(range(7,22+1))
s_times = [f'{str(i).zfill(2)}:00' for i in s_time_h_range] + [f'{str(i).zfill(2)}:30' for i in s_time_h_range] + ['23:00']
e_time_h_range = list(range(7,21+1))
e_times = [f'{str(i).zfill(2)}:00' for i in e_time_h_range] + [f'{str(i).zfill(2)}:30' for i in e_time_h_range] + ['06:30']
time_combos = [(i, j) for i in s_times for j in e_times]
full_combos = [i+j for i in date_combos for j in time_combos]

def selenium_title(combo):
    'selenium 하나 실행'
    # options = Options()
    # options.add_argument('--headless')
    driver = webdriver.Chrome()
    driver.maximize_window()
    title = driver.title
    rentcar_crawl(driver, *combo)
    driver.quit()
    return title

with futures.ThreadPoolExecutor() as executor: # default/optimized number of threads
    titles = list(executor.map(selenium_title, full_combos))