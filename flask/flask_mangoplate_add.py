from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from bs4 import BeautifulSoup

def get_mangoplate_info(keyword):
    url = f"https://www.mangoplate.com/search/{keyword}"

    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)  # run without GUI / without chrome window

    driver.get(url)

    req = driver.page_source
    soup = BeautifulSoup(req, "html.parser")
    info_list = soup.find_all(name="div", attrs={"class": "info"})  # store name address

    # Save the page address
    page_urls = []
    page_url_base = "https://www.mangoplate.com"  # base address + href

    for info in info_list:
        review_url = info.find(name="a")
        if review_url is not None:
            page_urls.append(page_url_base + review_url.get("href"))  # Create shop detail page url

    # Crawl the top 5 urls
    titles = []
    total_scores = []
    addresses = []
    menus = []

    for url in page_urls[0:5]:
        driver.get(url)

        # store name
        element = 'body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > header > div.restaurant_title_wrap > span > h1'  # copy selector
        title_raw = driver.find_element(By.CSS_SELECTOR, element)  # Extract value using selector in element
        title = title_raw.text  # change value to text
        titles.append(title)  # Save to list

        # grade
        element = 'body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > header > div.restaurant_title_wrap > span > strong > span'
        total_raw = driver.find_element(By.CSS_SELECTOR, element)
        total_score = total_raw.text
        total_scores.append(total_score)

        # Detailed Address
        element = 'body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table > tbody > tr:nth-child(1) > td > span.Restaurant__InfoAddress--Text'
        total_raw = driver.find_element(By.CSS_SELECTOR, element)
        address = total_raw.text
        addresses.append(address)

        # Representative menu
        from selenium.common.exceptions import NoSuchElementException

        element1 = 'body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table > tbody > tr:nth-child(2) > td > span'
        element2 = 'body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table > tbody > tr:nth-child(3) > td > span'

        try:
            total_raw = driver.find_element(By.CSS_SELECTOR, element1)
        except NoSuchElementException:
            try:
                total_raw = driver.find_element(By.CSS_SELECTOR, element2)
            except NoSuchElementException:
                total_raw = None

        if total_raw:
            menu = total_raw.text
            menus.append(menu)

    driver.quit()

    # Convert to data frame
    data = {
        'Title': titles,
        'Total Score': total_scores,
        'Address': addresses,
        'Menu': menus
    }
    df = pd.DataFrame(data)

    return df.to_dict('index')
