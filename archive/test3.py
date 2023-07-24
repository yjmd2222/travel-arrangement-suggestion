import time
import traceback
import csv

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from bs4 import BeautifulSoup

from itertools import combinations

def parse_date(date_: datetime):
    '''datetime 'yyyy-mm-dd' 형식 str으로 반환'''
    return date_.strftime(r"%Y-%m-%d")

def hotel_crawl(s_date: datetime, e_date: datetime):
    '입력한 시간/날짜에 따라 크롤링 진행'
    driver.get('https://www.booking.com/searchresults.ko.html?ss=%EC%A0%9C%EC%A3%BC%EB%8F%84%2C+%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&label=Korean_South_Korea-KO-KR-131246354044-lqHqiW6tNbRkHjsFQdmmhwS637818828162%3Apl%3Ata%3Ap1%3Ap2%3Aac%3Aap%3Aneg%3Afi%3Atidsa-1227182654382%3Alp1009842%3Ali%3Adec%3Adm%3Aag131246354044%3Acmp400536625&sid=1a2cdd5c26bf10a9c3ed2baaa7785c56&aid=318615&lang=ko&sb=1&src_elem=sb&src=index&dest_id=4170&dest_type=region&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure')

    print(f'{s_date}에서 {e_date} 숙박 조회시작')
    time.sleep(5)
    
    # 날짜 선택
    date_1 = driver.find_element(By.CLASS_NAME, 'b91c144835')
    date_1.click()
    time.sleep(0.5)

    # 시작일
    date_1 = driver.find_element(By.XPATH, rf'//*[@title="{s_date}"]')
    date_1.click()
    time.sleep(0.5)

    # 종료일
    date_2 = driver.find_element(By.XPATH, rf'//*[@title="{e_date}"]')
    date_2.click()
    time.sleep(0.5)

    # 적용하기 클릭
    done = driver.find_element(By.CLASS_NAME, 'fc63351294 a822bdf511 d4b6b7a9e7 cfb238afa1 c938084447 f4605622ad aa11d0d5cd')
    done.click()
    time.sleep(0.5)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    prod_list = soup.select('#dummy_prd_list section')

    hotel_csv(prod_list, s_date, e_date)
def get_date_combinations(start_date, days=30):
    'start_date부터 days일 후까지 가능한 시작/종료일 조합'
    date_list = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        date_list.append(current_date)
    
    combinations_list = list(combinations(date_list, 2))
    return combinations_list

def hotel_csv(prod_list, s_date, e_date):
    'csv로 저장'
    file_name = 'hotels.csv'
    file_exists = False

    # 이미 파일 있으면 추가하기 위한 작업
    try:
        with open(file_name, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            file_exists = any(row for row in reader) # 파일에 데이터가 있는지 확인합니다.
    except FileNotFoundError:
        pass

    data_list = []
    rental_dates = [s_date, e_date]
    for section in prod_list:
        hotel_name = section.select_one('.fcab3ed991 a23c043802 title').text.strip()
        region = section.select_one('.fcab3ed991 a23c043802 address').text.strip()
        ratings = float(section.select_one('.ico-star').next_sibling.strip())
        price = int(section.select_one('price-and-discounted-price').text.strip().replace(',',''))
        data_list.append([car_name,
                              region,
                              ratings,
                              price]
                              + rental_dates)

    with open('hotel.csv', 'a+', encoding='utf-8', newline='') as file:
        csv_writer = csv.writer(file)
        if not file_exists:
            csv_writer.writerow(columns)
        csv_writer.writerows(data_list)

if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.maximize_window()

    s_date = datetime.today() + timedelta(days=1)
    date_combos = get_date_combinations(s_date)

    for combo in date_combos:
        hotel_crawl(combo[0], combo[1])

    driver.quit()
