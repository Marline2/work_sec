
import api.contract as Contract
import api.models.Company as Company
import api.common.aws as Aws
import pandas as pd
import copy

from fastapi.responses import JSONResponse
from datetime import datetime
from fastapi import HTTPException
from bs4 import BeautifulSoup

def get_companies():
    try:
        # 한경뉴스에서 상위 20개 스크랩핑
        response = Contract.get_top20_sp500()
        soup = BeautifulSoup(response.text, 'html.parser')

        companies = []
        for i in range(0, 20):
            # 모든 'col1' 클래스를 가진 td를 한 번에 가져오고, 상위 20개만 사용
            symbol_tds = soup.find_all('td', class_='col1')
            if i-1 >= len(symbol_tds):
                continue
            symbol = symbol_tds[i-1].find('a').find('div', class_='symbol').text.strip()
            
            market_cap_tds = soup.find_all('td', class_='txt-rt col6 col-pc')
            market_cap = market_cap_tds[i-1].find('span').text.strip().replace(',', '')
            companies.append(Company.TopCompany(symbol=symbol, market_cap=float(market_cap)))
        #companies.sort(key=lambda x: x.market_cap, reverse=True) 시가총액 내림차순

        # SEC에서 회사 정보 추출
        response = Contract.get_sec_company()
        response_df = pd.DataFrame.from_dict(response, orient="index")[["cik_str", "title", "ticker"]]
        
        # symbol에 "." 기호가 있으면 "-"로 변경
        symbols = [company.symbol.replace('.', '-') for company in companies]
        print(f"총 symbol: {len(symbols)}")
        filtered_df = response_df[response_df["ticker"].isin(symbols)]
        print(f"매칭된 회사 수: {len(filtered_df)}")

        # 매칭 안된 회사 찾기
        # matched_symbols = set(filtered_df["ticker"])
        # unmatched_symbols = [s for s in symbols if s not in matched_symbols]
        # print(f"매칭 안된 회사: {unmatched_symbols}")

        result = []
        for _, row in filtered_df.iterrows():
            result.append(Company.Company(
                cik_str=str(row['cik_str']),
                title=row['title']
            ))
    
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"함수 내부 처리 오류: {e}")

def get_companyfacts(company_code: str, year: int):
    try:
        # SEC에서 데이터 가져오기
        response = Contract.get_sec_companyfacts(company_code)

        entity_name = response.get('entityName', 'N/A')
        facts = response.get('facts', {}).get('us-gaap', {})

        min_year = datetime.now().year - year
        records = []

        for concept_name, concept_data in facts.items():
            #description = concept_data.get('description', 'N/A')
            for unit, unit_data_list in concept_data.get('units', {}).items():
                for record in unit_data_list:
                    fy = record.get('fy')
                    if fy is not None and fy >= min_year:
                        records.append(Company.CompanyFactRecord(
                            # 재무항목이 LINE_ITEMS에 있으면 그대로, 없으면 call_deep_model로 번역 후 LINE_ITEMS와 translate_kr.py에 추가
                            company=entity_name,
                            company_number=company_code,
                            fin_item=concept_name, #재무항목
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

        # 열명 치환: 예시로 영문 -> 한글로 바꿔줌. 필요에 따라 매핑 수정
        csv_df = copy.deepcopy(res_df)

        # 열명만 변경 (치환)해서 DataFrame에 반영
        csv_df.columns = [
            "회사명" if col == "company" else
            "회사코드" if col == "company_number" else
            "재무항목" if col == "fin_item" else
            "단위" if col == "unit" else
            "값" if col == "value" else
            "시작일" if col == "start_date" else
            "종료일" if col == "end_date" else
            "회계연도" if col == "fis_year" else
            "회계분기" if col == "fis_quarter" else
            "공시서류" if col == "fil_document" else
            "제출일" if col == "fil_date" else
            "접수번호" if col == "accession_number" else col
            for col in csv_df.columns
        ]

        # 가져온 SEC 데이터를 엑셀 파일로 업로드하고, 다운로드 URL을 가져오기
        created_date = datetime.now().strftime("%Y%m%d")
        file_name = f"SEC_{entity_name.replace(' ', '_')}_{created_date}.csv"
        download_url = Aws.upload_csv_to_s3(csv_df, file_name) 

        # download_url을 result에 담고, res_df의 레코드 리스트를 따로 담아서 [{result}, {res_df}] 형태로 반환
        result = [{"download_url": download_url}]
 
        records = res_df.to_dict(orient="records") 
        return JSONResponse(content=[result, records]) 
        # 원본 데이터를 필요한 형태로 1차 가공 및 집계

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"함수 내부 처리 오류: {e}")