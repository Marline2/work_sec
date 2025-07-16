from datetime import datetime
from fastapi import FastAPI
import requests, pandas as pd

app = FastAPI()

HEADERS = {
    'User-Agent': "MyCompany MyName my.email@example.com",
    'From': 'my.email@example.com'
}
 

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}

# 회사명 및 코드
@app.get("/getCompanies/{capital_letter}")
def get_companies(capital_letter: str):
    res = requests.get("https://www.sec.gov/files/company_tickers.json",
                   headers={"User-Agent":"your@email.com"}).json()
    df = pd.DataFrame.from_dict(res, orient="index")
    df_selected = df[["cik_str", "title"]]

    # initial_letter로 시작하는 title만 필터링
    filtered_df = df_selected[df_selected["title"].str.startswith(capital_letter, na=False)]
    return filtered_df.to_dict(orient="records")

# 회사명 받아오면 company 코드 가져오기
@app.get("/getCompanyFacts/{company_code}/{year}/")
def say_hello(company_code: str, year: int):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{company_code}.json"
    try:
        print(f"[{company_code}] 데이터를 요청합니다...")
        response = requests.get(url, headers=HEADERS)
        print('res')
        response.raise_for_status()

        data = response.json()
        entity_name = data.get('entityName', 'N/A')
        facts = data.get('facts', {}).get('us-gaap', {})

        print(facts)

        min_year = datetime.now().year - year
        records = []

        for concept_name, concept_data in facts.items():
            description = concept_data.get('description', 'N/A')
            for unit, unit_data_list in concept_data.get('units', {}).items():
                for record in unit_data_list:
                    fy = record.get('fy')
                    if fy is not None and fy >= min_year:
                        records.append({
                            # 재무항목이 LINE_ITEMS에 있으면 그대로, 없으면 call_deep_model로 번역 후 LINE_ITEMS와 translate_kr.py에 추가
                            "company": entity_name,
                            "company_number": company_code,
                            "fin_item": concept_name, #재무항목목
                            #"항목설명": description,
                            "unit": unit,
                            "value": record.get('val'),
                            "start_date": record.get('start'),
                            "end_date": record.get('end'),
                            "fis_year": fy, #회계연도
                            "fis_quarter": record.get('fp'), # 회계분기
                            "fil_document": record.get('form'), # 공시서류
                            "fil_date": record.get('filed'), # 제출일
                            "accession_number": record.get('accn') #접수번호
                            })
                        
        res = pd.DataFrame(records)
        res.sort_values(by='제출일', ascending=False, inplace=True)
        # 추후 aws에 엑셀 csv 다운로드경로 내보내기

    except requests.exceptions.HTTPError as e:
        print(f"🚨 [{company_code}] HTTP 오류: {e}\n")
        return {f"message":"HTTP 오류: {e}"}
    except Exception as e:
        print(f"🚨 [{company_code}] 처리 중 오류: {e}\n")
        return {f"message":"처리 오류: {e}"}

    return res.to_dict(orient="records")