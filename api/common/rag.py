# import os
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import google.generativeai as genai
# import numpy as np
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_core.documents import Document
# import aws as Aws

# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=GOOGLE_API_KEY)

# # 청크화
# def chunk_article_with_langchain(article_text: str,
#                                  title: str,
#                                  chunk_size: int = 500,
#                                  chunk_overlap: int = 100) -> list[str]:

#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         separators=["\n\n", "\n", " ", ""],
#         length_function=len,
#         is_separator_regex=False,
#     )
#     chunks = text_splitter.split_text(article_text)

#     documents_with_metadata = []
#     for i, chunk in enumerate(chunks):
#         doc = Document(
#             page_content=chunk,
#             metadata={
#                 "article_title": title,
#                 "chunk_index": i # 0부터 시작하는 인덱스
#             }
#         )
#     documents_with_metadata.append(doc)
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

#     original_data = Aws.get_s3_to_json('NEWS_NVIDIA_20250722.json')
#     print(original_data)
#     print("--- 텍스트 청크화 시작 ---")
#     # 청크를 할때 메타데이터도 삽입
#     all_chunks = []
#     for article in original_data:
#         paragraphs = article.get("paragraphs", "")
#         title = article.get("title", "")
#         if paragraphs:
#             chunks = chunk_article_with_langchain(paragraphs, title, chunk_size=500, chunk_overlap=100)
#             all_chunks.extend(chunks)
#             print(f"총 청크 개수: {len(all_chunks)}")

#     print(all_chunks)

#     # print("\n--- 청크 임베딩 시작 (Gemini API 사용) ---")
#     # chunk_embeddings = embed_chunks_with_gemini(article_chunks, model_name='models/embedding-001')

#     # if chunk_embeddings.size > 0: # 임베딩이 성공적으로 생성되었는지 확인
#     #     print(f"\n--- 임베딩 결과 ---")
#     #     print(f"생성된 임베딩의 형태: {chunk_embeddings.shape}")
#     #     print("첫 번째 청크의 임베딩 (일부):")
#     #     print(chunk_embeddings[0][:10]) # 첫 번째 청크의 임베딩 중 앞부분 10개 값만 출력
#     #     print("...")
#     # else:
#     #     print("\n임베딩이 생성되지 않았습니다. 오류 메시지를 확인하세요.")