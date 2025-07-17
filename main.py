from fastapi import FastAPI, status 
from typing import List

import api.uitls as utils
import api.models.Company as Company
import api.models.Response as Response

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}

# S&P500 상위 회사 시가 총액으로 20개 추출
@app.get("/getCompanies", response_model=List[Company.Company], status_code=status.HTTP_200_OK,
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
@app.get("/getCompanyFacts/{sec_code}/{year}/", response_model=List[Company.CompanyFactRecord], status_code=status.HTTP_200_OK,
         responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def get_companyfacts(sec_code: str, year: int):
    # SEC에서 데이터 가져오기
    response = utils.get_companyfacts(sec_code, year)
    return response

@app.get("/getFinData/{ticker_code}/", response_model=List[Company.YahooFinClosePrice], status_code=status.HTTP_200_OK,
         responses={
        # 예외 상황을 Swagger UI에 명시
        400: {"description": "잘못된 요청 (Invalid Input)", "model": Response.ErrorResponseModel}, # 또는 에러 모델
        404: {"description": "리소스를 찾을 수 없음 (Not Found)", "model": Response.ErrorResponseModel},
        500: {"description": "서버 내부 오류 (Internal Server Error)", "model": Response.ErrorResponseModel}
        # 필요하다면 다른 상태 코드도 추가 (예: 403 Forbidden, 401 Unauthorized 등)
    })
def get_fin_data(ticker_code: str):
    # SEC에서 데이터 가져오기
    response = utils.get_fin_data(ticker_code)
    return response