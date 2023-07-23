import csv
import time

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException)
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

from itertools import combinations

columns = ['url', 'hotel_name','region','ratings', 'price', 'start_date', 'end_date', 'page_idx', 'cap_idx']

def parse_date(date_: datetime):
    '''datetime 'yyyy-mm-dd' 형식 str으로 반환'''
    return date_.strftime(r"%Y-%m-%d")

def try_find_element(driver, *args, click=False, find_all=False):
    '''
    셀레니움 element 찾기 try-except wrapper로 구성\n
    *args: (by, value)들로 구성된 튜플 -> ((by, value),)\n
    find_all은 모든 element 찾기\n
    click은 single element에 대해 click. None 반환\n
    None이 아닌 경우는 element 또는 element list 반환
    '''
    while True:
        count = 0
        try:
            for tuple_ in args:
                if find_all:
                    return driver.find_elements(*tuple_)
                else:
                    element = driver.find_element(*tuple_)
                    if click:
                        element.click()
                    else:
                        return element
            break
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException) as error:
            count += 1
            if count == 3:
                print('팝업 종료 시도 3회 실패')
                raise Exception
            # print(f'팝업 종료 시도. 에러: {type(error).__name__}')
            try:
                close_popup = driver.find_element(By.XPATH, r'//*[@aria-label="로그인 혜택 안내 창 닫기."]')
                close_popup.click()
            except Exception as error:
                print(f'에러: {type(error).__name__}, 메시지: {error}')
    return None

def hotel_crawl(driver, s_date: datetime, e_date: datetime, page_idx_=-1, cap_idx_=-1):
    '''
    입력한 시간/날짜에 따라 크롤링 진행\n
    page_idx_: 오류 난 페이지. 0에서 3. -1이면 전부 오류 또는 오류 없음
    '''
    s_date_str = parse_date(s_date)
    e_date_str = parse_date(e_date)

    print(f'{s_date_str}에서 {e_date_str} 숙박 조회시작. 페이지: {page_idx_}')

    time.sleep(5)
    # 날짜 박스 + 시작 + 종료일 클릭
    try_find_element(driver, (By.XPATH, '//*[@data-testid="date-display-field-start"]'), (By.XPATH, rf'//*[@data-date="{s_date_str}"]'), (By.XPATH, rf'//*[@data-date="{e_date_str}"]'), click=True)

    # 인원수 박스, 인원 증가/감소 선택
    # 감소 버튼 class: fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e c334e6f658 e1b7cfea84 cd7aa7c891
    # 증가 버튼 class: fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e c334e6f658 e1b7cfea84 d64a4ea64d
    cap_box_css = '.d47738b911.b7d08821c3'
    dec_css = '.'+'fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e c334e6f658 e1b7cfea84 cd7aa7c891'.replace(' ', '.')
    inc_css = '.'+'fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e c334e6f658 e1b7cfea84 d64a4ea64d'.replace(' ', '.')
    # 1명
    try_find_element(driver, (By.CSS_SELECTOR, cap_box_css), (By.CSS_SELECTOR, dec_css), click=True)
    for cap_idx in range(4):
        if cap_idx == 0:
            # 1인 포함 조회할 때: 1명은 loop 직전에 pass 선택 완료
            if cap_idx_ in (0,-1):
                pass
            # 다른 인원수 조회해야 하는 경우
            else:
                continue
        else:
            # 오류난 페이지 cap 재설정: idx 일치할 때까지 + 클릭
            if cap_idx_ == cap_idx:
                try_find_element(driver, (By.CSS_SELECTOR, inc_css)*cap_idx, click=True)
            # 전부 조회하는 경우 하나씩
            elif cap_idx_ == -1:
                try_find_element(driver, (By.CSS_SELECTOR, inc_css), click=True)
            # 해당사항 없음
            else:
                continue

        # 적용하기 클릭
        try_find_element(driver, (By.XPATH, r'//*[@type="submit"]'), click=True)

        # 페이지 번호 elements
        time.sleep(5)
        # page_num_elements = try_find_element(driver, (By.CSS_SELECTOR, '.fc63351294.f9c5690c58'), find_all=True) # 가끔 notInteractable이나 staleElement 오류 남

        # 다음 페이지로 넘김
        for page_idx in range(4):
            if page_idx == 0:
                # 오류난 페이지 재시도: page_idx_가 page_idx번째(0번째) 또는 -1이면 진행해야 하므로 pass
                if page_idx_ in (0, -1):
                    pass
                # 0번째가 아니고 -1이 아니면
                else:
                    continue
            else:
                # 오류난 페이지 재시도: page_idx_가 page_idx번째(1,2,3번째)거나 -1이면 진행해야 하므로 pass
                if page_idx_ in (page_idx, -1):
                    pass
                else:
                    continue
                script_scroll_down = 'window.scrollTo(0, document.body.scrollHeight);'
                driver.execute_script(script_scroll_down)
                try:
                    element = driver.find_element(By.CSS_SELECTOR, f"button.fc63351294.f9c5690c58[aria-label=' {page_idx+1}']")
                    element.click()
                except Exception as error:
                    print(f'페이지 넘김 실패. 에러: {error}')
                    with open('failed_times_pages.txt', 'a+', encoding='utf-8') as file:
                        file.write(','.join([type(error).__name__]+[date.strftime(r'%Y-%m-%d %H:%M') for date in (s_date, e_date)]+[str(page_idx), str(cap_idx)])+'\n')
                    continue

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            time.sleep(15)
            
            hotels = soup.select('.a826ba81c4.fa2f36ad22.afd256fc79.d08f526e0d.ed11e24d01.ef9845d4b3.da89aeb942')

            hotel_csv(hotels, s_date, e_date, page_idx, cap_idx)

def get_date_combinations(start_date, days=30):
    'start_date부터 days일 후까지 가능한 시작/종료일 조합'
    date_list = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        date_list.append(current_date)
    
    combinations_list = list(combinations(date_list, 2))
    return combinations_list

def hotel_csv(soup_elements, s_date, e_date, page_idx, cap_idx):
    'csv로 저장'
    s_date_str = parse_date(s_date)
    e_date_str = parse_date(e_date)
    file_name = f'data/raw/hotels/{s_date_str}_{e_date_str}_{page_idx}_{cap_idx}.csv'

    data_list = []
    stay_length_dates = [s_date_str, e_date_str]
    indices = [page_idx, cap_idx]
    error_count = 0
    for property_card in soup_elements:
        try:
            url = property_card.find('a', class_='e13098a59f')['href'].strip()
            hotel_name = property_card.select_one('[data-testid="title"]').text.strip()
            region = property_card.select_one('[data-testid="address"]').text.strip()
            ratings = float(property_card.select_one('.b5cd09854e.d10a6220b4').text.strip())
            price = int(property_card.select_one('[data-testid="price-and-discounted-price"]').text.strip().replace(',','').replace('₩',''))
            data_list.append([url,
                            hotel_name,
                            region,
                            ratings,
                            price]
                            +stay_length_dates
                            +indices)
        except:
            error_count += 1
            if error_count == 25:
                print('property-card 모두 비어있음')
                with open('failed_times_pages.txt', 'a+', encoding='utf-8') as file:
                    file.write(','.join(['empty_element']+[date.strftime(r'%Y-%m-%d %H:%M') for date in (s_date, e_date)]+[str(page_idx), str(cap_idx)])+'\n')


    with open(file_name, 'a+', encoding='utf-8', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        csv_writer.writerow(columns)
        csv_writer.writerows(data_list)

if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(r'https://www.booking.com/searchresults.ko.html?ss=%EC%A0%9C%EC%A3%BC%EB%8F%84%2C+%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&label=gen173nr-1FCAQoggJCEHNlYXJjaF_soJzso7zrj4RIF1gEaH2IAQGYARe4ARfIAQzYAQHoAQH4AQOIAgGoAgO4At_456UGwAIB0gIkNjZjMzFmMjktN2Q2NC00ZGI3LThlZDAtNTkzYWUzZWExNzNh2AIF4AIB&sid=b065785ade8dcdd3291c771274ed42bd&aid=304142&lang=ko&sb=1&src_elem=sb&src=index&dest_id=4170&dest_type=region&ac_position=0&ac_click_type=b&ac_langcode=ko&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=7465539e6ff801f0&ac_meta=GhA3NDY1NTM5ZTZmZjgwMWYwIAAoATICa286BuygnOyjvEAASgBQAA%3D%3D&checkin=2023-07-28&checkout=2023-07-29&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure')
    driver.implicitly_wait(3)

    s_date = datetime.today() + timedelta(days=1)
    date_combos = get_date_combinations(s_date)

    for combo in date_combos:
        hotel_crawl(driver, combo[0], combo[1])

    driver.quit()

    