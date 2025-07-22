# 0. 필요한 라이브러리 설치 (최초 1회만 실행)
# pip install langchain-text-splitters langchain-google-genai langchain-chroma google-generativeai

import os
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document # 청크를 Document 객체로 다루기 위함

# --- 1. 환경 설정 ---
# Google API 키 설정
# 직접 코드에 입력하는 대신 환경 변수를 사용하는 것이 더 안전하고 권장됩니다.
# 예: export GOOGLE_API_KEY="YOUR_API_KEY" (터미널에서 설정)
# 또는 os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY" (코드에서 직접 설정, 보안 유의)
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다. API 키를 설정해주세요.")

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Google 임베딩 모델 지정
EMBEDDING_MODEL = "models/text-embedding-004" # 또는 'models/embedding-001' 등 사용 가능한 모델
# Google LLM (답변 생성용) 지정
GENERATION_MODEL = "gemini-pro" # 또는 'gemini-1.5-pro-latest' 등 사용 가능한 모델

# ChromaDB 저장 경로
CHROMA_DB_PATH = "./chroma_db"

print("--- 환경 설정 완료 ---")

# --- 2. 대용량 기사 데이터 로드 및 청크화 ---
# 실제 기사 내용은 파일에서 읽어오거나 API로 가져오는 경우가 많습니다.
# 여기서는 예시를 위해 긴 문자열을 사용합니다.

large_article_text = """
최근 인공지능(AI) 기술은 전례 없는 속도로 발전하며 우리 사회 전반에 걸쳐 혁명적인 변화를 가져오고 있습니다.
특히 대규모 언어 모델(LLM)은 자연어 처리(NLP) 분야에서 놀라운 성과를 보이며, 인간과의 자연스러운 대화, 문서 요약, 번역 등 다양한 응용 분야에서 활용되고 있습니다.
이러한 LLM의 발전은 단순히 기술적인 진보를 넘어, 산업 구조, 교육 방식, 심지어 일상생활의 모습까지 근본적으로 바꾸고 있습니다.

AI 기술의 핵심에는 방대한 데이터를 학습하여 패턴을 인식하고 새로운 정보를 생성하는 능력이 있습니다.
초기 AI는 특정 작업에 특화된 좁은 인공지능(Narrow AI) 형태였지만, 이제는 일반 인공지능(AGI)을 향한 연구가 활발히 진행되고 있습니다.
AGI는 인간과 유사한 수준의 인지 능력을 갖추고 다양한 문제를 해결할 수 있는 AI를 목표로 합니다.

하지만 AI 기술의 발전과 함께 윤리적, 사회적 문제에 대한 논의도 활발해지고 있습니다.
개인 정보 보호, 알고리즘 편향, 일자리 감소 문제, AI의 오남용 가능성 등 다양한 우려의 목소리가 나오고 있습니다.
이에 따라 AI 개발 및 활용에 있어 투명성, 공정성, 책임성을 확보하기 위한 규제와 가이드라인 마련의 중요성이 강조되고 있습니다.
많은 국가와 국제기구들이 AI 윤리 원칙을 수립하고 있으며, 기술 개발과 사회적 수용 사이의 균형을 찾는 노력이 계속되고 있습니다.

미래 사회에서 AI는 더욱 중요한 역할을 할 것으로 예상됩니다.
자율주행 자동차, 스마트 팩토리, 정밀 의료, 지능형 로봇 등 AI 기반의 혁신적인 제품과 서비스가 등장하여 우리의 삶을 더욱 풍요롭게 만들 것입니다.
동시에 인간과 AI가 공존하며 상호 보완적인 관계를 맺는 새로운 패러다임이 요구됩니다.
AI를 단순한 도구가 아닌, 인간의 창의성과 생산성을 증진시키는 파트너로 활용하는 지혜가 필요합니다.
결론적으로 AI는 양날의 검과 같지만, 신중하고 윤리적인 접근을 통해 인류의 발전에 기여할 수 있는 무한한 잠재력을 가지고 있습니다.
우리는 이 강력한 기술의 긍정적인 면을 극대화하고, 부정적인 영향을 최소화하기 위한 지속적인 노력을 기울여야 합니다.
"""

# 텍스트 스플리터 초기화
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # 각 청크의 최대 글자 수
    chunk_overlap=200,    # 청크 간 겹치는 글자 수 (문맥 유지를 위해)
    length_function=len,  # 글자 수 기준으로 분할
    add_start_index=True, # 원본 문서에서의 시작 인덱스 추가 (선택 사항)
)

# Document 객체 리스트 생성
# LangChain의 VectorStore는 Document 객체 리스트를 기대합니다.
# page_content는 실제 텍스트, metadata는 추가 정보 (여기서는 원본 텍스트의 제목 등으로 활용 가능)
chunks = [Document(page_content=large_article_text, metadata={"source": "example_article", "title": "AI 기술의 현재와 미래"})]
chunks = text_splitter.split_documents(chunks)

print(f"--- 기사 청크화 완료: 총 {len(chunks)}개의 청크 생성 ---")
# for i, chunk in enumerate(chunks):
#    print(f"청크 {i+1} (길이: {len(chunk.page_content)}): {chunk.page_content[:100]}...")

# --- 3. Google 임베딩 모델로 임베딩 생성 ---
# LangChain에서 Google Generative AI 임베딩 모델을 사용합니다.
# 이 클래스가 내부적으로 genai.configure(api_key=...) 설정을 활용합니다.
embeddings_model = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

print(f"--- 임베딩 모델 '{EMBEDDING_MODEL}' 초기화 완료 ---")

# --- 4. 임베딩 및 청크를 벡터 데이터베이스에 저장 ---
# ChromaDB를 사용하며, 이전에 저장된 데이터가 있다면 로드하고, 없으면 새로 생성합니다.
# vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings_model)
# print("이전 데이터베이스 로드 또는 새 데이터베이스 생성 중...")

# 새 데이터를 추가하는 경우 from_documents를 사용합니다.
# 기존에 데이터베이스가 존재하면 여기에 추가됩니다.
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings_model,
    persist_directory=CHROMA_DB_PATH
)

# 데이터베이스 영속화 (저장)
vectorstore.persist()
print(f"--- 청크와 임베딩이 ChromaDB '{CHROMA_DB_PATH}'에 성공적으로 저장되었습니다. ---")

# --- 5. RAG (Retrieval-Augmented Generation)를 통한 검색 및 답변 생성 (예시) ---
# 저장된 데이터를 활용하여 질문에 답변하는 과정을 시뮬레이션합니다.

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# RAG 시스템을 위한 LLM 초기화
llm = ChatGoogleGenerativeAI(model=GENERATION_MODEL, temperature=0.7)

# 프롬프트 템플릿 정의 (검색된 문서를 LLM에 전달하는 방식)
prompt = ChatPromptTemplate.from_messages([
    ("system", "제공된 맥락 정보를 사용하여 질문에 답변하세요. 만약 정보가 충분하지 않다면, '제공된 정보로는 답변할 수 없습니다.'라고 말하세요.\n\n{context}"),
    ("human", "{input}"),
])

# 문서 체인 (검색된 문서를 프롬프트에 채워넣는 역할)
document_chain = create_stuff_documents_chain(llm, prompt)

# 리트리버 설정 (벡터스토어에서 유사 문서를 검색)
retriever = vectorstore.as_retriever()

# 최종 RAG 체인 생성
retrieval_chain = create_retrieval_chain(retriever, document_chain)

print("\n--- RAG 시스템 준비 완료 ---")

# 질문 예시
questions = [
    "AI 기술의 핵심은 무엇인가요?",
    "AI 발전과 함께 논의되는 윤리적, 사회적 문제는 무엇인가요?",
    "미래 사회에서 AI의 역할은 무엇으로 예상되나요?",
    "블록체인이 AI 발전에 어떤 영향을 미치나요?" # 관련 없는 질문
]

for i, question in enumerate(questions):
    print(f"\n--- 질문 {i+1}: {question} ---")
    response = retrieval_chain.invoke({"input": question})
    print("AI 답변:")
    print(response["answer"])

print("\n--- 모든 작업 완료 ---")