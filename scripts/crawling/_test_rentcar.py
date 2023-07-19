import time

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from bs4 import BeautifulSoup

from itertools import combinations

def parse_date(date_: datetime, time_: str):
    '''날짜('%Y%m%d'), 시간('%H:%M') 입력받아 SK렌트카 날짜 형식에 맞춰 변환'''
    date_ = date_.strftime(r'%Y%m%d') # datetime->str
    datetime_ = datetime.strptime(date_+time_, r"%Y%m%d%H:%M") # str->datetime
    day = datetime_.strftime(r"%d")
    suffix = "th"
    if day.endswith("1") and not day.endswith("11"):
        suffix = "st"
    elif day.endswith("2") and not day.endswith("12"):
        suffix = "nd"
    elif day.endswith("3") and not day.endswith("13"):
        suffix = "rd"

    # 앞에는 'Wednesday, August 9th, 2023'
    # 뒤에는 sql에 입력할 수 있는 timestamp
    return datetime_.strftime(f"%A, %B {day}{suffix}, %Y"), datetime_.timestamp()

def rentcar(s_date, e_date, s_time, e_time):
    '''
    s_date, e_date: datetime\n
    s_time, e_time: str('HH:MM')
    '''
    s_date, s_timestamp = parse_date(s_date, s_time)
    e_date, e_timestamp = parse_date(e_date, e_time)

    # sleep
    time.sleep(5)

    # 날짜 선택할 selector 클릭
    date_select_button = driver.find_element(By.CLASS_NAME, 'ico_date')
    date_select_button.click()
    time.sleep(0.5)

    # 시작일
    date_1 = driver.find_element(By.XPATH, rf'//*[@aria-label="Choose {s_date}"]')
    date_1.click()
    time.sleep(0.5)

    # 종료일
    date_2 = driver.find_element(By.XPATH, rf'//*[@aria-label="Choose {e_date}"]')
    date_2.click()
    time.sleep(0.5)

    # 시작 시각
    rent_time = driver.find_element(By.XPATH, r'//*[text()="대여시간"]/following-sibling::select')
    rent_time_select = Select(rent_time)
    rent_time_select.select_by_value(s_time)
    time.sleep(0.5)

    # 종료 시각
    rent_time = driver.find_element(By.XPATH, r'//*[text()="반납시간"]/following-sibling::select')
    rent_time_select = Select(rent_time)
    rent_time_select.select_by_value(e_time)
    time.sleep(0.5)

    # 일정 선택완료 클릭
    done = driver.find_element(By.XPATH, r'//*[text()="일정 선택완료"]')
    done.click()
    time.sleep(0.5)

    # 차량 조회하고 예약하기 클릭
    search = driver.find_element(By.XPATH, r'//*[text()="차량 조회하고 예약하기"]')
    search.click()
    time.sleep(3)

    # html parse
    html = driver.page_source
    soup = BeautifulSoup(html)

    # SK렌트카에서 구분지은 블록들
    dill_box_wraps = soup.find_all(class_='dill_box_wrap')

    # 각 블록마다
    for wrap in dill_box_wraps:
        # 브랜드
        print(wrap.find(class_='car_enter').text)
        # 각 블록 안에 렌트 가능한 차량
        for item in wrap.find_all(class_='list_item'):
            print(item)
            print()

def get_date_combinations(start_date, days):
    'start_date부터 days일 후까지 가능한 시작/종료일 조합'
    date_list = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        date_list.append(current_date)
    
    combinations_list = list(combinations(date_list, 2))
    return combinations_list

# s_time == 07:30-22:00, e_time == 06:00-21:00
s_time_h_range = list(range(8,22))
s_times = [f'{i}:00' for i in s_time_h_range] + [f'{i}:30' for i in s_time_h_range] + ['7:30', '22:00']
e_time_h_range = list(range(6,21))
e_times = [f'{i}:00' for i in e_time_h_range] + [f'{i}:30' for i in e_time_h_range] + ['21:00']

if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.get('https://homepage.skcarrental.com/')
    driver.maximize_window()

    s_date = datetime.today() + timedelta(days=1)
    DAYS= 60
    date_combos = get_date_combinations(s_date, DAYS)

    rentcar(date_combos[5][0], date_combos[5][1], s_times[2], e_times[6])

    # for combo in date_combos:
    #     for s_time in s_times:
    #         for e_time in e_times:
    #             rentcar(combo[0], combo[1], s_time, e_time)

    driver.quit()