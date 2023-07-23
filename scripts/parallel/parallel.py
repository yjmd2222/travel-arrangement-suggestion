from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent import futures
from datetime import datetime, timedelta

def selenium_title(combo, func, link, wait, indices=[-1,-1]):
    'selenium 하나 실행'
    try:
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        driver.get(link)
        driver.implicitly_wait(wait)
    except Exception as error:
        print(f'에러: {type(error).__name__}, 메시지: {error}')
        with open('failed_times.txt', 'a+', encoding='utf-8') as file:
            file.write(','.join([type(error).__name__]+[date.strftime(r'%Y-%m-%d %H:%M') for date in combo])+'\n')
            return None
    try:
        func(driver, *combo, *indices)
    except Exception as error:
        print(f'에러: {type(error).__name__}, 메시지: {error}')
        with open('failed_times.txt', 'a+', encoding='utf-8') as file:
            file.write(','.join([type(error).__name__]+[date.strftime(r'%Y-%m-%d %H:%M') for date in combo])+'\n')
            return None
    title = driver.title
    driver.quit()
    return title

if __name__ == '__main__':

    def parallel_hotel_crawling():
        '전체 데이터 크롤링'
        import os
        import shutil
        from sys import path
        path.append('scripts/crawling')
        from crawling_hotel_capacity import hotel_crawl, get_date_combinations

        s_date = datetime.today() + timedelta(days=1)
        date_combos = get_date_combinations(s_date, 33)

        with futures.ThreadPoolExecutor() as executor:
            titles = list(executor.map(lambda x: selenium_title(x,
                                                                hotel_crawl,
                                                                r'https://www.booking.com/searchresults.ko.html?ss=%EC%A0%9C%EC%A3%BC%EB%8F%84%2C+%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&label=gen173nr-1FCAQoggJCEHNlYXJjaF_soJzso7zrj4RIF1gEaH2IAQGYARe4ARfIAQzYAQHoAQH4AQOIAgGoAgO4At_456UGwAIB0gIkNjZjMzFmMjktN2Q2NC00ZGI3LThlZDAtNTkzYWUzZWExNzNh2AIF4AIB&sid=b065785ade8dcdd3291c771274ed42bd&aid=304142&lang=ko&sb=1&src_elem=sb&src=index&dest_id=4170&dest_type=region&ac_position=0&ac_click_type=b&ac_langcode=ko&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=7465539e6ff801f0&ac_meta=GhA3NDY1NTM5ZTZmZjgwMWYwIAAoATICa286BuygnOyjvEAASgBQAA%3D%3D&checkin=2023-07-28&checkout=2023-07-29&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure',
                                                                5), date_combos))
        fail_logs = ['failed_times.txt', 'failed_times_pages.txt']
        reloc_failed_logs = ['data/raw/'+log for log in fail_logs]
        for idx in range(2):
            if os.path.exists(fail_logs[idx]):
                shutil.copy(fail_logs[idx], reloc_failed_logs[idx])
                os.remove(fail_logs[idx])

    def parallel_hotel_crawling_failed():
        '실패한 데이터 크롤링 시도'
        import os
        import shutil
        from sys import path
        from datetime import datetime
        path.append('scripts/crawling')
        from crawling_hotel_capacity import hotel_crawl

        def parse_datetime_tuple(s):
            # 문자열을 분리하여 datetime 구성 요소 추출
            parts = s.strip().split(',')[1:]
            # parts = [date[18:].split(', ') for date in parts]
            date_combo = [datetime.strptime(date, r'%Y-%m-%d %H:%M') for date in parts[:2]]
            idx_combo = [int(idx_) for idx_ in parts[2:]]
            return tuple(date_combo), idx_combo

        date_combos = []
        idx_combos = []
        dates_path = 'data/raw/failed_times_pages.txt'

        with open(dates_path, 'r') as file:
            for line in file:
                data_combo, idx_combo = parse_datetime_tuple(line)
                date_combos.append(data_combo)
                idx_combos.append(idx_combo)

        with futures.ThreadPoolExecutor() as executor:
            titles = list(executor.map(lambda x, y: selenium_title(x,
                                                                   hotel_crawl,
                                                                   r'https://www.booking.com/searchresults.ko.html?ss=%EC%A0%9C%EC%A3%BC%EB%8F%84%2C+%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&label=gen173nr-1FCAQoggJCEHNlYXJjaF_soJzso7zrj4RIF1gEaH2IAQGYARe4ARfIAQzYAQHoAQH4AQOIAgGoAgO4At_456UGwAIB0gIkNjZjMzFmMjktN2Q2NC00ZGI3LThlZDAtNTkzYWUzZWExNzNh2AIF4AIB&sid=b065785ade8dcdd3291c771274ed42bd&aid=304142&lang=ko&sb=1&src_elem=sb&src=index&dest_id=4170&dest_type=region&ac_position=0&ac_click_type=b&ac_langcode=ko&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=7465539e6ff801f0&ac_meta=GhA3NDY1NTM5ZTZmZjgwMWYwIAAoATICa286BuygnOyjvEAASgBQAA%3D%3D&checkin=2023-07-28&checkout=2023-07-29&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure',
                                                                   5,
                                                                   y), date_combos, idx_combos))
        fail_logs = ['failed_times.txt', 'failed_times_pages.txt']
        reloc_fail_logs = ['data/raw/'+log for log in fail_logs]
        for idx in range(2):
            if os.path.exists(fail_logs[idx]):
                shutil.copy(fail_logs[idx], reloc_fail_logs[idx])
                os.remove(fail_logs[idx])
            elif os.path.exists(reloc_fail_logs[idx]):
                os.remove(reloc_fail_logs[idx])

    # parallel_hotel_crawling()
    parallel_hotel_crawling_failed()
