from fastapi import FastAPI, status 
from typing import List

import api.uitls as utils
import api.models.Company as Company

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}

# S&P500 상위 회사 시가 총액으로 20개 추출
@app.get("/getCompanies", response_model=List[Company.Company], status_code=status.HTTP_200_OK)
def get_top_sp500_companies():
    response = utils.get_companies()
    return response

# 회사명 받아오면 company 코드 가져오기
@app.get("/getCompanyFacts/{company_code}/{year}/", response_model=List[Company.CompanyFactRecord], status_code=status.HTTP_200_OK)
def get_companyfacts(company_code: str, year: int):
    # SEC에서 데이터 가져오기
    response = utils.get_companyfacts(company_code, year)
    return response