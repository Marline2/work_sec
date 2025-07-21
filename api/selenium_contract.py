from selenium.webdriver.common.by import By
from seleniumbase import SB
from dotenv import load_dotenv
import os
import time

load_dotenv()

reuters_id = os.getenv('REUTERS_ID')
reuters_pw = os.getenv('REUTERS_PW')

# 로터스에서 스크랩핑
def get_reuters_fin_news(search: str):

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
        sb.save_screenshot_to_logs(name="after_login") 
        # 로그인 종료

        sb.open(search_urls)
        #sb.uc_gui_handle_captcha()
        time.sleep(5)

        articles = []
        base_url = "https://www.reuters.com"
        #one_month_ago = datetime.utcnow() - timedelta(days=30)
        # ul 태그: class가 search-results__list__* 인 것
        ul_elements = sb.find_elements(By.CSS_SELECTOR, '[class^="search-results__list__"]')
        print(ul_elements)
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
                    "title": title,
                    "url": href,
                    "date": pub_date_str
                })

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
    #ui 클래스 search-results__list__* 로 검색해서
    # 그 안에 있는 li의 첫번째 div에서 time태그 datatime을 가져와. 
    # 예시는 2025-07-02T11:23:51Z인데 현재로부터 3달 전만 긁자.
    # 당장은 한달치로 할거니까 그럴필요는 없음.
    # li의 두 번째 div에서 value로 (text) 제목 가져오고 href도 가져온다.
    # https://www.reuters.com/ 이게 기본으로 있다. 붙여서 가져와야함.
    # 모든 li를 긁었으면 search-results__pagination__* div 속의 두 번째 버튼을 누른다.
    # div 안의 span 값도 긁어오면 좋다. 1 to 17 of 17 만약 2와 3번째 값이 다르면 계속 누르고 긁어오게 for문을
    # 돌려야한다. 