from selenium import webdriver
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
    try:
        driver = webdriver.Chrome()
    except Exception as error:
        print(f'에러: {type(error).__name__}, 메시지: {error}')
    driver.maximize_window()
    try:
        rentcar_crawl(driver, *combo)
    except Exception as error:
        print(f'에러: {type(error).__name__}, 메시지: {error}')
    title = driver.title
    driver.quit()
    return title

with futures.ThreadPoolExecutor() as executor:
    titles = list(executor.map(selenium_title, full_combos))