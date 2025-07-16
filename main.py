from datetime import datetime
from fastapi import FastAPI
import requests, pandas as pd
from pydantic import BaseModel
from typing import List, Optional

class Company(BaseModel):
    """회사 기본 정보 모델"""
    cik_str: int
    title: str

class CompanyFactRecord(BaseModel):
    """회사 재무 정보 상세 기록 모델"""
    company: str
    company_number: str
    fin_item: str
    unit: str
    value: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    fis_year: Optional[int] = None
    fis_quarter: Optional[str] = None
    fil_document: Optional[str] = None
    fil_date: Optional[datetime] = None
    accession_number: Optional[str] = None

app = FastAPI()

HEADERS = {
    'User-Agent': "1MyCompany MyName my.emai1l@example.com",
    'From': '1my.email@example.com'
}
 

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}

# 회사명 및 코드
@app.get("/getCompanies/{capital_letter}", response_model=List[Company])
def get_companies(capital_letter: str):
    res = requests.get("https://www.sec.gov/files/company_tickers.json",
                   headers={"User-Agent":"your@email.com"}).json()
    df = pd.DataFrame.from_dict(res, orient="index")
    df_selected = df[["cik_str", "title"]]

    # initial_letter로 시작하는 title만 필터링
    filtered_df = df_selected[df_selected["title"].str.startswith(capital_letter, na=False)]
    # initial_letter로 시작하는 title만 필터링
    companies = [
        Company(cik_str=int(row["cik_str"]), title=row["title"])
        for _, row in filtered_df.iterrows()
    ]
    return companies

# 회사명 받아오면 company 코드 가져오기
@app.get("/getCompanyFacts/{company_code}/{year}/", response_model=List[CompanyFactRecord])
def say_hello(company_code: str, year: int):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{company_code}.json"
    try:
        print(f"[{company_code}] 데이터를 요청합니다...")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status() # 4xx 또는 5xx 응답 코드에 대해 HTTPError 발생

        data = response.json()
        entity_name = data.get('entityName', 'N/A')
        facts = data.get('facts', {}).get('us-gaap', {})

        min_year = datetime.now().year - year
        records = []

        for concept_name, concept_data in facts.items():
            description = concept_data.get('description', 'N/A')
            for unit, unit_data_list in concept_data.get('units', {}).items():
                for record in unit_data_list:
                    fy = record.get('fy')
                    if fy is not None and fy >= min_year:
                        records.append(CompanyFactRecord(
                            # 재무항목이 LINE_ITEMS에 있으면 그대로, 없으면 call_deep_model로 번역 후 LINE_ITEMS와 translate_kr.py에 추가
                            company=entity_name,
                            company_number=company_code,
                            fin_item=concept_name, #재무항목목
                            #"항목설명": description,
                            unit=unit,
                            value=record.get('val'),
                            start_date=record.get('start'),
                            end_date=record.get('end'),
                            fis_year=fy, #회계연도
                            fis_quarter=record.get('fp'), # 회계분기
                            fil_document=record.get('form'), # 공시서류
                            fil_date=record.get('filed'), # 제출일
                            accession_number=record.get('accn') #접수번호
                        ))

        res_df = pd.DataFrame([r.dict() for r in records])
        if 'fil_date' in res_df.columns and not res_df['fil_date'].isnull().all():
            res_df.sort_values(by='fil_date', ascending=False, inplace=True)
        # 추후 aws에 엑셀 csv 다운로드경로 내보내기

    except requests.exceptions.HTTPError as e:
        print(f"🚨 [{company_code}] HTTP 오류: {e}\n")
        return {f"message":"HTTP 오류: {e}"}
    except Exception as e:
        print(f"🚨 [{company_code}] 처리 중 오류: {e}\n")
        return {f"message":"처리 오류: {e}"}
    return res_df.to_dict(orient="records")