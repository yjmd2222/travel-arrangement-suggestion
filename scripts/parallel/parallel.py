from selenium import webdriver
from concurrent import futures
from datetime import datetime, timedelta

def selenium_title(combo, func, link, wait):
    'selenium 하나 실행'
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(link)
        driver.implicitly_wait(wait)
    except Exception as error:
        print(f'에러: {type(error).__name__}, 메시지: {error}')
        with open('failed_times', 'a+', encoding='utf-8') as file:
            file.write(str(combo)+'\n')
            return None
    try:
        func(driver, *combo)
    except Exception as error:
        print(f'에러: {type(error).__name__}, 메시지: {error}')
        with open('failed_times', 'a+', encoding='utf-8') as file:
            file.write(str(combo)+'\n')
            return None
    title = driver.title
    driver.quit()
    return title

if __name__ == '__main__':

    from sys import path
    path.append('scripts/crawling')
    from crawling_hotel import hotel_crawl, get_date_combinations

    s_date = datetime.today() + timedelta(days=1)
    date_combos = get_date_combinations(s_date)

    with futures.ThreadPoolExecutor() as executor:
        titles = list(executor.map(lambda x: selenium_title(x,
                                                            hotel_crawl,
                                                            r'https://www.booking.com/searchresults.ko.html?ss=%EC%A0%9C%EC%A3%BC%EB%8F%84%2C+%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&label=gen173nr-1FCAQoggJCEHNlYXJjaF_soJzso7zrj4RIF1gEaH2IAQGYARe4ARfIAQzYAQHoAQH4AQOIAgGoAgO4At_456UGwAIB0gIkNjZjMzFmMjktN2Q2NC00ZGI3LThlZDAtNTkzYWUzZWExNzNh2AIF4AIB&sid=14dedff24ad71b3922a2f34073ee4036&aid=304142&lang=ko&sb=1&src_elem=sb&src=index&dest_id=4170&dest_type=region&checkin=2023-07-20&checkout=2023-07-21&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure',
                                                            5), date_combos))
