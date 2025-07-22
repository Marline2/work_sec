from pydantic import BaseModel
from typing import Optional

class TopCompany(BaseModel):
    """S&P500 상위 20개 추출"""
    symbol: str
    market_cap : float # 시가총액

class Company(BaseModel):
    """회사 기본 정보 모델"""
    sec_code: str
    ticker_code: str
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
    fil_date: Optional[str] = None
    accession_number: Optional[str] = None

class YahooFinClosePrice(BaseModel):
    """야후핀에서 가져오는 종가 모델"""
    date: str
    close_value: float

class CollectNews(BaseModel):
    """Aplha에서 긁어온 뉴스 기사"""
    title: str
    url: str
    date: str
    sentiment: str

class NewsAPI(BaseModel):
    """NewsAPI에서 긁어온 뉴스 기사"""
    title: str
    url: str
    image: str
    publish: str
    content: str