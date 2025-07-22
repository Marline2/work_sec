# import os
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import google.generativeai as genai
# import numpy as np

# # 중요: YOUR_API_KEY_HERE 부분을 실제 발급받은 Google API 키로 대체하세요.
# # 보안을 위해 환경 변수로 설정하는 것을 강력히 권장합니다.
# # 예: os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE"
# # 또는 ~/.bashrc, ~/.zshrc 등에 export GOOGLE_API_KEY="YOUR_API_KEY_HERE" 추가 후 터미널 재시작
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# if not GOOGLE_API_KEY:
#     raise ValueError(
#         "Google API 키가 설정되지 않았습니다. "
#         "환경 변수 'GOOGLE_API_KEY'를 설정하거나 코드 내 GOOGLE_API_KEY 변수에 직접 입력하세요."
#     )

# # Generative AI 모델 구성
# genai.configure(api_key=GOOGLE_API_KEY)

# def chunk_article_with_langchain(article_text: str,
#                                  chunk_size: int = 500,
#                                  chunk_overlap: int = 100) -> list[str]:
#     """
#     Langchain의 RecursiveCharacterTextSplitter를 사용하여 영문 기사를 청크로 나눕니다.

#     Args:
#         article_text (str): 청크화할 영문 기사 텍스트.
#         chunk_size (int): 각 청크의 최대 문자 수.
#         chunk_overlap (int): 인접한 청크 간의 중복 문자 수.

#     Returns:
#         list[str]: 청크로 나뉜 텍스트 문자열 리스트.
#     """
#     print(f"Langchain의 RecursiveCharacterTextSplitter를 사용하여 기사를 청크로 나누는 중...")
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         separators=["\n\n", "\n", " ", ""],
#         length_function=len,
#         is_separator_regex=False,
#     )
#     chunks = text_splitter.split_text(article_text)
#     print(f"총 {len(chunks)}개의 청크가 생성되었습니다.")
#     return chunks

# def embed_chunks_with_gemini(chunks: list[str], model_name: str = 'models/embedding-001') -> np.ndarray:
#     """
#     주어진 텍스트 청크 리스트를 'gemini-embedding-001' 모델로 임베딩합니다.

#     Args:
#         chunks (list[str]): 임베딩할 텍스트 청크 리스트.
#         model_name (str): 사용할 Gemini 임베딩 모델의 이름. 기본값은 'models/embedding-001'.

#     Returns:
#         np.ndarray: 각 청크에 대한 임베딩 벡터를 포함하는 NumPy 배열.
#     """
#     print(f"'{model_name}' 모델을 사용하여 임베딩을 생성 중입니다...")
#     embeddings = []
    
#     # Gemini Embedding API는 한 번에 여러 청크를 처리할 수 있습니다.
#     # 하지만 API 호출 제한을 고려하여 적절한 배치 크기를 설정하는 것이 좋습니다.
#     # 여기서는 편의상 전체 청크를 한 번에 보내는 예시를 보여드립니다.
#     # 실제 사용 시에는 chunks를 작은 배치(batch)로 나누어 호출하는 것을 고려하세요.
#     # 예: for i in range(0, len(chunks), batch_size):
#     #         batch = chunks[i:i + batch_size]
#     #         response = genai.embed_content(model=model_name, content=batch)
#     #         embeddings.extend([item['value'] for item in response['embedding']])
            
#     try:
#         response = genai.embed_content(
#             model=model_name,
#             content=chunks,
#         )
#         # embed_content가 리스트를 반환하는 경우에 맞게 처리
#         # 각 아이템이 딕셔너리이고 'value' 키를 가진다고 가정
#         embeddings = np.array([item['value'] for item in response])
#         print("임베딩 생성 완료.")
#         return embeddings
#     except Exception as e:
#         if isinstance(e, TypeError) and "string indices must be integers" in str(e):
#             print("임베딩 API 응답 형식이 예상과 다릅니다. 반환값이 리스트가 아닌 문자열일 수 있습니다.")
#             print("API 응답 구조를 확인하거나, 'embed_content' 함수의 반환값을 점검하세요.")
#         else:
#             print(f"임베딩 생성 중 오류 발생: {e}")
#             print("Google API 키가 올바르게 설정되었는지, Generative Language API가 활성화되었는지 확인하세요.")
#         return np.array([]) # 빈 배열 반환 또는 오류 처리

# if __name__ == "__main__":
#     # 예시로 사용할 긴 영문 기사 텍스트
#     long_article = """
#     Artificial intelligence (AI) is rapidly transforming various aspects of our lives,
#     from healthcare to finance and entertainment. Its capabilities are expanding at an unprecedented pace,
#     driven by advancements in machine learning, deep learning, and neural networks.
#     AI systems can now perform tasks that were once thought to be exclusive to human intelligence,
#     such as natural language understanding, image recognition, and complex problem-solving.

#     One of the most significant applications of AI is in natural language processing (NLP).
#     NLP allows computers to understand, interpret, and generate human language.
#     This technology powers virtual assistants like Siri and Google Assistant,
#     translation services, and sentiment analysis tools.
#     The development of large language models (LLMs) has further revolutionized NLP,
#     enabling more nuanced and context-aware interactions.

#     In healthcare, AI is being used to diagnose diseases more accurately,
#     discover new drugs, and personalize treatment plans.
#     For instance, AI algorithms can analyze medical images like X-rays and MRIs
#     to detect anomalies that might be missed by the human eye.
#     This can lead to earlier diagnosis and more effective interventions.
#     However, ethical considerations and data privacy remain key challenges in this domain.

#     The financial sector also heavily relies on AI for fraud detection,
#     algorithmic trading, and risk assessment. AI models can analyze vast amounts of financial data
#     to identify suspicious patterns and predict market trends.
#     This helps financial institutions make more informed decisions and protect their assets.
#     Despite its benefits, the increasing reliance on AI in finance raises concerns about systemic risks
#     and the potential for biased algorithms.

#     As AI continues to evolve, its impact on society will only grow.
#     It presents both immense opportunities for innovation and significant challenges
#     related to employment, ethics, and governance.
#     Ensuring that AI is developed and deployed responsibly will be crucial
#     for maximizing its benefits while mitigating its risks.
#     Public discourse and policy-making will play a vital role in shaping the future of AI.
#     """

#     print("--- 텍스트 청크화 시작 ---")
#     article_chunks = chunk_article_with_langchain(long_article, chunk_size=500, chunk_overlap=100)

#     print("\n--- 생성된 청크 미리보기 ---")
#     for i, chunk in enumerate(article_chunks[:3]): # 처음 3개의 청크만 출력
#         print(f"\n--- 청크 {i+1} ---")
#         print(chunk)
#         if len(article_chunks) > 3 and i == 2:
#             print("...")

#     print("\n--- 청크 임베딩 시작 (Gemini API 사용) ---")
#     chunk_embeddings = embed_chunks_with_gemini(article_chunks, model_name='models/embedding-001')

#     if chunk_embeddings.size > 0: # 임베딩이 성공적으로 생성되었는지 확인
#         print(f"\n--- 임베딩 결과 ---")
#         print(f"생성된 임베딩의 형태: {chunk_embeddings.shape}")
#         print("첫 번째 청크의 임베딩 (일부):")
#         print(chunk_embeddings[0][:10]) # 첫 번째 청크의 임베딩 중 앞부분 10개 값만 출력
#         print("...")
#     else:
#         print("\n임베딩이 생성되지 않았습니다. 오류 메시지를 확인하세요.")