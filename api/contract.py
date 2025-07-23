import requests
from fastapi import HTTPException
import yfinance as yf
import pandas as pd
from datetime import datetime
#from api.models.Company import YahooFinClosePrice
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from newsapi import NewsApiClient
from eventregistry import *


import os

load_dotenv()

aplgha_key = os.getenv('ALPHAVANTAGE_KEY')
news_api_key = os.getenv('NEWS_API_KEY')
event_api_key = os.getenv('EVENT_API_KEY')


HEADERS = {
    'User-Agent': "1MyCompany MyName my.emai1l@example.com",
    'From': '1my.email@example.com'
}

# 한경뉴스에서 스크랩핑
def get_top20_sp500():
    # 20순위 추출
    try:
        url = "https://www.hankyung.com/globalmarket/usa-stock-sp500"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return response
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 500
        raise HTTPException(
            status_code=status_code,
            detail=f"한경닷컴에서 데이터를 가져오는 중 HTTP 오류 발생: {e.response.reason}"
        )
    except requests.exceptions.RequestException as e:
        # HTTPError 외의 requests 관련 모든 예외 (연결 오류, 타임아웃 등) 처리
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"한경닷컴 연결 오류 또는 응답 없음: {e}"
        )
    except Exception as e:
        # 예상치 못한 기타 모든 예외 처리
        raise HTTPException(
            status_code=500,
            detail=f"알 수 없는 오류 발생: {e}"
        )
    
# SEC에서 회사 정보 얻기
def get_sec_company():
    # 20순위 추출
    try:
        response = requests.get("https://www.sec.gov/files/company_tickers.json",
                   headers={"User-Agent":"your@email.com"}).json()
        return response
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 500
        raise HTTPException(
            status_code=status_code,
            detail=f"SEC에서 데이터를 가져오는 중 HTTP 오류 발생: {e.response.reason}"
        )
    except requests.exceptions.RequestException as e:
        # HTTPError 외의 requests 관련 모든 예외 (연결 오류, 타임아웃 등) 처리
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"SEC 연결 오류 또는 응답 없음: {e}"
        )
    except Exception as e:
        # 예상치 못한 기타 모든 예외 처리
        raise HTTPException(
            status_code=500,
            detail=f"통신 중, 알 수 없는 오류 발생: {e}"
        )
    
# SEC에서 스크랩핑
def get_sec_companyfacts(company_code: str):
    try:
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{company_code}.json"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

        return response.json()
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 500
        raise HTTPException(
            status_code=status_code,
            detail=f"SEC에서 데이터를 가져오는 중 HTTP 오류 발생: {e.response.reason}"
        )
    except requests.exceptions.RequestException as e:
        # HTTPError 외의 requests 관련 모든 예외 (연결 오류, 타임아웃 등) 처리
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"SEC 연결 오류 또는 응답 없음: {e}"
        )
    except Exception as e:
        # 예상치 못한 기타 모든 예외 처리
        raise HTTPException(
            status_code=500,
            detail=f"통신 중, 알 수 없는 오류 발생: {e}"
        )
    
# 야후핀에서 스크랩핑
def get_yahoofin_close_price(company_code: str, start_date: str, end_date: str):
    try:
        all_data = []

        asset = yf.Ticker(company_code)
        label = asset.info.get('shortName', company_code)
        df = asset.history(start=start_date, end=end_date)
        df = df[['Close']].rename(columns={'Close': label})
        df.index = df.index.tz_localize(None)  # 시간대 정보 제거

        # Date 인덱스를 컬럼으로 변환하고 문자열로 yyyy-mm-dd 포맷으로 변환
        df = df.reset_index()
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

        for _, row in df.iterrows():
            all_data.append(
                YahooFinClosePrice(
                    date=row['Date'],
                    close_value=float(row[label])
                )
            )

        return all_data
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 500
        raise HTTPException(
            status_code=status_code,
            detail=f"야후핀에서 데이터를 가져오는 중 HTTP 오류 발생: {e.response.reason}"
        )
    except requests.exceptions.RequestException as e:
        # HTTPError 외의 requests 관련 모든 예외 (연결 오류, 타임아웃 등) 처리
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"야후핀 연결 오류 또는 응답 없음: {e}"
        )
    except Exception as e:
        # 예상치 못한 기타 모든 예외 처리
        raise HTTPException(
            status_code=500,
            detail=f"야후핀 통신 중, 알 수 없는 오류 발생: {e}"
        )
    
# Alphavantage 뉴스 및 감성분석 호출
def get_alpha_sentiment_analysis(company_code: str):
    try:
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={company_code}&apikey={aplgha_key}"
        response = requests.get(url)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

        return response.json()
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 500
        raise HTTPException(
            status_code=status_code,
            detail=f"Alpha에서 데이터를 가져오는 중 HTTP 오류 발생: {e.response.reason}"
        )
    except requests.exceptions.RequestException as e:
        # HTTPError 외의 requests 관련 모든 예외 (연결 오류, 타임아웃 등) 처리
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"Alpha 연결 오류 또는 응답 없음: {e}"
        )
    except Exception as e:
        # 예상치 못한 기타 모든 예외 처리
        raise HTTPException(
            status_code=500,
            detail=f"통신 중, 알 수 없는 오류 발생: {e}"
        )
    
def get_news_api(query: str, page: int):
    newsapi = NewsApiClient(api_key=news_api_key)
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        all_articles = newsapi.get_everything(q=query,
                                              sources='bloomberg, reuters, bbc-news, the-verge, business-insider',
                                              language='en',
                                              to=today_str,
                                              sort_by='publishedAt',
                                              page_size=20,
                                              page=page)
            
        return all_articles
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 500
        raise HTTPException(
            status_code=status_code,
            detail=f"News api에서 데이터를 가져오는 중 HTTP 오류 발생: {e.response.reason}"
        )
    except requests.exceptions.RequestException as e:
        # HTTPError 외의 requests 관련 모든 예외 (연결 오류, 타임아웃 등) 처리
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"News api 연결 오류 또는 응답 없음: {e}"
        )
    except Exception as e:
        # 예상치 못한 기타 모든 예외 처리
        raise HTTPException(
            status_code=500,
            detail=f"통신 중, 알 수 없는 오류 발생: {e}"
        )

def get_headline_news_api(query:str, page: int):
    newsapi = NewsApiClient(api_key=news_api_key)
    try:
        all_articles = newsapi.get_top_headlines(
                                              q=query,
                                              sources='bloomberg, reuters',
                                              page_size=20,
                                              page=page)
            
        return all_articles
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 500
        raise HTTPException(
            status_code=status_code,
            detail=f"News api에서 데이터를 가져오는 중 HTTP 오류 발생: {e.response.reason}"
        )
    except requests.exceptions.RequestException as e:
        # HTTPError 외의 requests 관련 모든 예외 (연결 오류, 타임아웃 등) 처리
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"News api 연결 오류 또는 응답 없음: {e}"
        )
    except Exception as e:
        # 예상치 못한 기타 모든 예외 처리
        raise HTTPException(
            status_code=500,
            detail=f"통신 중, 알 수 없는 오류 발생: {e}"
        )

def get_event_news_api(query: str, page: int):
    #er = EventRegistry(apiKey=event_api_key)
    #q = QueryArticles(conceptUri=er.getConceptUri("finance"), lang="eng", allowUseOfArchive = False)
    request_body = {
            "action": "getArticles",
            "keyword": query,
            "articlesPage": page,
            "articlesCount": 20,
            "articlesSortBy": "date",
            "articlesSortByAsc": False,
            "dataType": [
                "news"
            ],
            "lang":["eng"],
            "forceMaxDataTimeWindow": 31,
            "resultType": "articles",
            "apiKey": event_api_key
        }
    json_payload = json.dumps(request_body)
    
    try:
        response = requests.post('https://eventregistry.org/api/v1/article/getArticles', 
                                 data=json_payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status() # Raise an exception for bad status codes
        response.encoding = 'utf-8'
        response_data = response.json()
   
        res = []
        for article in response_data.get('articles', {}).get('results', []):
            obj = {
                "title": article.get('title', 'N/A'),
                "content": (article.get('body', 'N/A')[:200] + '...') if article.get('body') and len(article.get('body')) > 200 else article.get('body', 'N/A'),
                "url": article.get('url', 'N/A'),
                "image": article.get('image', 'N/A'),
                "publish": article.get('dateTimePub', 'N/A'),
                "source": article.get('source', {}).get('title', 'N/A')
            }
            res.append(obj)

        return res
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 500
        raise HTTPException(
            status_code=status_code,
            detail=f"News api에서 데이터를 가져오는 중 HTTP 오류 발생: {e.response.reason}"
        )
    except requests.exceptions.RequestException as e:
        # HTTPError 외의 requests 관련 모든 예외 (연결 오류, 타임아웃 등) 처리
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"News api 연결 오류 또는 응답 없음: {e}"
        )
    except Exception as e:
        # 예상치 못한 기타 모든 예외 처리
        raise HTTPException(
            status_code=500,
            detail=f"통신 중, 알 수 없는 오류 발생: {e}"
        )