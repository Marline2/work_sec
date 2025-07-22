from datetime import datetime
from selenium.webdriver.common.by import By
from seleniumbase import SB
from dotenv import load_dotenv
import re
import os
import time

load_dotenv()

reuters_id = os.getenv('REUTERS_ID')
reuters_pw = os.getenv('REUTERS_PW')

# 로터스 구조 1, 상위 20개만 NEWS 데이터에 저장
# 로터스 구조 2, 전체 기사를 특정 기간에만 긁기
# 로터스에서 스크랩핑
def get_reuters_stock_news(search: str):

    login_urls = "https://www.reuters.com/account/sign-in/"

    search_urls = f"https://www.reuters.com/site-search/?query={search}&section=markets&date=past_month"
    with SB(uc=True, test=True) as sb:
        # 로그인
        sb.uc_open_with_reconnect(login_urls, reconnect_time=5)
        sb.type('#email', reuters_id)
        # 'Next'라는 텍스트를 가진 span을 찾음
        # INSERT_YOUR_CODE
        # 이메일 입력 후 'Next' 버튼이 활성화될 때까지 대기
        next_element = sb.find_elements(By.CSS_SELECTOR, '[class^="sign-in-form__form-buttons-container__"]')[0]\
            .find_element(By.CSS_SELECTOR, 'button:nth-of-type(2)')
        # 버튼 클릭
        next_element.click()
        time.sleep(2)
        sb.type('#password', reuters_pw)
        sign_btn = sb.find_elements(By.CSS_SELECTOR, '[class^="sign-in-form__form-buttons-container__"]')[0]\
            .find_element(By.CSS_SELECTOR, 'button:nth-of-type(2)')

        sign_btn.click()
        time.sleep(5)
        # 로그인 종료

        sb.open(search_urls)
        #sb.uc_gui_handle_captcha()
        time.sleep(5)

        articles = []
        base_url = "https://www.reuters.com"
        #one_month_ago = datetime.utcnow() - timedelta(days=30)
        # ul 태그: class가 search-results__list__* 인 것
        page_elements = sb.find_elements(By.CSS_SELECTOR, '[class^="search-results__pagination__"]')
        numbers = list(map(int, re.findall(r'\d+', page_elements[0].text)))
        # 맨 마지막 리스트 요소 date가 start_date보다 낮을 경우 추가 필요
        while numbers[1] <= numbers[2]:
            ul_elements = sb.find_elements(By.CSS_SELECTOR, '[class^="search-results__list__"]')
            for ul in ul_elements:
                li_elements = ul.find_elements(By.TAG_NAME, 'li')
                for li in li_elements:
                    divs = li.find_elements(By.TAG_NAME, 'div')

                    time_tag = divs[0].find_element(By.TAG_NAME, 'time')
                    pub_date_str = time_tag.get_attribute('datetime')

                    a_tag = divs[1].find_element(By.TAG_NAME, 'a')
                    title = a_tag.text.strip()
                    href = a_tag.get_attribute('href')
                    if not href.startswith("http"):
                        href = base_url + href

                    articles.append({
                        "date": pub_date_str,
                        "title": title,
                        "url": href
                    })
            if numbers[1] == numbers[2]:
                break
            # 다음 페이지 버튼 (두 번째 버튼)을 클릭
            page_elements[0].find_elements(By.CSS_SELECTOR, "button")[1].click()
            time.sleep(5)

            page_elements = sb.find_elements(By.CSS_SELECTOR, '[class^="search-results__pagination__"]')
            numbers = list(map(int, re.findall(r'\d+', page_elements[0].text)))
            print(f"페이지 이동 후 numbers: {numbers}")

        print(len(articles))
        # INSERT_YOUR_CODE
        for article in articles:
            print(article['title'])
            article_url = article["url"]
            sb.open(article_url)
            time.sleep(5)
            # 모든 div[data-testid^="paragraph-"] 태그를 찾음
            paragraph_divs = sb.find_elements(By.CSS_SELECTOR, 'div[data-testid^="paragraph-"]')
            paragraph_texts = []
            for div in paragraph_divs:
                text = div.text.strip()
                paragraph_texts.append(text)
            # paragraphs를 하나의 string으로 합치고, 따옴표 없이 연결
            article["paragraphs"] = ' '.join(paragraph_texts).replace(', opens new tab', '')
    return articles

# 전체 기사를 특정 기간에만 긁기
def get_reuters_fin_news(start_date: str):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    login_urls = "https://www.reuters.com/account/sign-in/"

    search_urls = f"https://www.reuters.com/business/finance/"
    with SB(uc=True, test=True) as sb:
        # 로그인
        sb.uc_open_with_reconnect(login_urls, reconnect_time=5)
        sb.type('#email', reuters_id)
        # 'Next'라는 텍스트를 가진 span을 찾음
        # INSERT_YOUR_CODE
        # 이메일 입력 후 'Next' 버튼이 활성화될 때까지 대기
        next_element = sb.find_elements(By.CSS_SELECTOR, '[class^="sign-in-form__form-buttons-container__"]')[0]\
            .find_element(By.CSS_SELECTOR, 'button:nth-of-type(2)')
        # 버튼 클릭
        next_element.click()
        time.sleep(2)
        sb.type('#password', reuters_pw)
        sign_btn = sb.find_elements(By.CSS_SELECTOR, '[class^="sign-in-form__form-buttons-container__"]')[0]\
            .find_element(By.CSS_SELECTOR, 'button:nth-of-type(2)')

        sign_btn.click()
        time.sleep(5)
        # 로그인 종료

        sb.open(search_urls)
        #sb.uc_gui_handle_captcha()
        time.sleep(5)

        articles = []
        base_url = "https://www.reuters.com"
        #one_month_ago = datetime.utcnow() - timedelta(days=30)
        # ul 태그: class가 search-results__list__* 인 것

        # 미리 Load more 해두기
        while True:
            # 더보기 버튼        
            load_elements = sb.find_elements(By.CSS_SELECTOR, '[class^="topic__loadmore__"]')[0]\
                    .find_elements(By.TAG_NAME, 'button')[0]

            # 맨 마지막 요소의 날짜 확인
            ul_elements = sb.find_elements(By.CSS_SELECTOR, '[class^="story-collection__three_columns__"]')[0]\
                            .find_elements(By.TAG_NAME, 'li')[-1].find_elements(By.TAG_NAME, 'div')

            time_tag = ul_elements[0].find_element(By.TAG_NAME, 'time')
            pub_date_str = time_tag.get_attribute('datetime')
            # pub_date_str 예: '2025-07-18T17:28:02Z'
            pub_date_only = pub_date_str.split('T')[0]  # '2025-07-18'
            pub_date = datetime.strptime(pub_date_only, "%Y-%m-%d")
                # start_date보다 작아지면 break
            if pub_date >= start_date:
                load_elements.click()
                time.sleep(3)
            else:
                break

        ul_elements = sb.find_elements(By.CSS_SELECTOR, '[class^="story-collection__one_hero_and_one_column__"]')

        for ul in ul_elements:
            li_elements = ul.find_elements(By.TAG_NAME, 'li')
            for li in li_elements:
                divs = li.find_elements(By.TAG_NAME, 'div')

                time_tag = divs[0].find_element(By.TAG_NAME, 'time')
                pub_date_str = time_tag.get_attribute('datetime')

                a_tag = divs[1].find_element(By.TAG_NAME, 'a')
                href = a_tag.get_attribute('href')
                if not href.startswith("http"):
                    href = base_url + href

                articles.append({
                    "date": pub_date_str,
                    "url": href
                })
        print(len(articles))

        ul_elements = sb.find_elements(By.CSS_SELECTOR, '[class^="story-collection__four_columns__"]')
        for ul in ul_elements:
            li_elements = ul.find_elements(By.TAG_NAME, 'li')
            for li in li_elements:
                divs = li.find_elements(By.TAG_NAME, 'div')

                time_tag = divs[0].find_element(By.TAG_NAME, 'time')
                pub_date_str = time_tag.get_attribute('datetime')

                a_tag = divs[1].find_element(By.TAG_NAME, 'a')
                href = a_tag.get_attribute('href')
                if not href.startswith("http"):
                    href = base_url + href

                articles.append({
                    "date": pub_date_str,
                    "url": href
                })
        print(len(articles))
        ul_elements = sb.find_elements(By.CSS_SELECTOR, '[class^="story-collection__three_columns__"]')
        for ul in ul_elements:
            li_elements = ul.find_elements(By.TAG_NAME, 'li')
            for li in li_elements:
                divs = li.find_elements(By.TAG_NAME, 'div')

                time_tag = divs[0].find_element(By.TAG_NAME, 'time')
                pub_date_str = time_tag.get_attribute('datetime')

                a_tag = divs[1].find_element(By.TAG_NAME, 'a')
                href = a_tag.get_attribute('href')
                if not href.startswith("http"):
                    href = base_url + href

                articles.append({
                    "date": pub_date_str,
                    "url": href
                })
            

        print(len(articles))

        i = 0
        while i < len(articles):
            date_str = articles[i]['date'].split('T')[0]
            article_date = datetime.strptime(date_str, "%Y-%m-%d")
            if article_date < start_date:
                del articles[i]
            else:
                i += 1
        print(articles)

        for article in articles:
            article_url = article["url"]
            sb.open(article_url)
            time.sleep(5)
            # 모든 div[data-testid^="paragraph-"] 태그를 찾음
            paragraph_divs = sb.find_elements(By.CSS_SELECTOR, 'div[data-testid^="paragraph-"]')
            paragraph_texts = []
            for div in paragraph_divs:
                text = div.text.strip()
                paragraph_texts.append(text)
            # paragraphs를 하나의 string으로 합치고, 따옴표 없이 연결
            # 타이틀도 이곳에 넣자.
            article["title"] = sb.find_element(By.CSS_SELECTOR, 'h1[data-testid^="Heading"]').text
            article["paragraphs"] = ' '.join(paragraph_texts).replace(', opens new tab', '')
    return articles