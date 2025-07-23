from fastapi import FastAPI, status, Path
from typing import List, Optional

import api.uitls as utils
import api.models.Company as Company
import api.models.Response as Response
from eventregistry import *


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}

# S&P500 상위 회사 시가 총액으로 20개 추출 후 csv 저장
@app.post("/uploadCompanyList", summary="S&P500 시가 총액 상위인 20개의의 회사를 저장합니다. (프론트는 호출하지 않습니다.)", status_code=status.HTTP_200_OK,
                 responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def upload_company_list():
    response = utils.upload_company_list()
    return response

@app.get("/getEventNewsAPI/{page}", summary="News API를 사용하여 뉴스 정보를 가져옵니다.", response_model=List[Company.NewsAPI], status_code=status.HTTP_200_OK,
         responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def get_event_news_api(page: int, query: str = None):
    # SEC에서 데이터 가져오기
    """
        호출 예시:
        - 검색어 없이:   /getEventNewsAPI/1
        - 검색어 포함:   /getEventNewsAPI/1?query=검색어
    """
    response = utils.get_event_news_api(page, query)
    return response

@app.get("/getNewsAPI/{query}/{page}", summary="News API를 사용하여 뉴스 정보를 가져옵니다.", response_model=List[Company.NewsAPI], status_code=status.HTTP_200_OK,
         responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def get_news_api(query: str, page: int):
    # SEC에서 데이터 가져오기
    response = utils.get_news_api(query, page)
    return response

@app.get("/getHeadlineNewsAPI/{page}", summary="News API를 사용하여 헤드라인 뉴스 정보를 가져옵니다.", response_model=List[Company.NewsAPI], status_code=status.HTTP_200_OK,
         responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def get_headline_news_api(
    page: int,
    query: str = None
):
    """
    호출 예시:
    - 검색어 없이:   /getHeadlineNewsAPI/1
    - 검색어 포함:   /getHeadlineNewsAPI/1?query=검색어
    """
    # SEC에서 데이터 가져오기
    response = utils.get_headline_news_api(query, page)
    return response

@app.get("/uploadReutersNews", summary="(용량 부족으로 실행 불가) 최근 1개월의 기사를 로이터에서 수집하고 저장합니다. (프론트를 호출하지 않습니다.)", status_code=status.HTTP_200_OK,
         responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def upload_rueters_news():
    # SEC에서 데이터 가져오기
    response = utils.upload_rueters_news()
    return response

@app.get("/uploadReutersNewsAll/{start_date}", summary="(용량 부족으로 실행 불가) 최대 최근 1개월의 전체 기사를 로이터에서 수집하고 저장합니다. (프론트를 호출하지 않습니다.)", status_code=status.HTTP_200_OK,
         responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def upload_all_rueters_news(start_date: str= Path(
        ..., # 필수 파라미터임을 나타냅니다.
        description="""
            기사 수집 시작일입니다. 입력 형식은 'YYYY-MM-DD' 입니다.
        """
    )):
    # SEC에서 데이터 가져오기
    response = utils.upload_all_rueters_news(start_date)
    return response


# S&P500 상위 회사 시가 총액으로 20개 추출
@app.get("/getCompanies", summary="S&P500 시가 총액 상위인 20개의 회사를 가져옵니다. ", response_model=List[Company.Company], status_code=status.HTTP_200_OK,
        responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    }
         )
def get_top_sp500_companies():
    response = utils.get_companies()
    return response

# 회사명 받아오면 company 코드 가져오기
@app.get("/getCompanyFacts/{sec_code}/{years_ago}/", summary="SEC에서 회사 정보를 가져옵니다. ", response_model=List[Company.CompanyFactRecord], status_code=status.HTTP_200_OK,
         responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def get_companyfacts(sec_code: str, years_ago : int = Path(
        ..., # 필수 파라미터임을 나타냅니다.
        description="""
            현재로부터 몇 년 전 데이터를 가져올지 나타냅니다. \n
            1년 전부터면 숫자 1을 넣으시면 됩니다. 숫자 5를 넣으면 5년 전부터의 데이터를 가져옵니다.
        """
    )):
    # SEC에서 데이터 가져오기
    response = utils.get_companyfacts(sec_code, years_ago)
    return response

@app.get("/getFinData/{ticker_code}/{years_ago}/", summary="기간에 해당되는 주식 종가를 가져옵니다. ", response_model=List[Company.YahooFinClosePrice], status_code=status.HTTP_200_OK,
         responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def get_fin_data(ticker_code: str, years_ago: int = Path(
        ..., # 필수 파라미터임을 나타냅니다.
        description="""
            현재로부터 몇 년 전 데이터를 가져올지 나타냅니다. \n
            1년 전부터면 숫자 1을 넣으시면 됩니다. 숫자 5를 넣으면 5년 전부터의 데이터를 가져옵니다.
        """
    )):
    # SEC에서 데이터 가져오기
    response = utils.get_fin_data(ticker_code, years_ago)
    return response

@app.get("/getSentimentAnalysis/{ticker_code}/", summary="최근 기사 50개와 매수 점수를 가져옵니다. ", response_model=List[Company.CollectNews], status_code=status.HTTP_200_OK,
         responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def get_sentiment_analysis(ticker_code: str):
    # SEC에서 데이터 가져오기
    response = utils.get_sentiment_analysis(ticker_code)
    return response