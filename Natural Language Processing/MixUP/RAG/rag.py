# build_db_local.py
import pandas as pd
import numpy as np
import chromadb
import os

def build_vector_db():
    # 1. 파일 로드
    print("데이터 로딩 중...")
    df = pd.read_csv("data/train_dataset.csv")
    embeddings = np.load("rag/embeddings.npy") # Colab에서 가져온 파일

    if "section" not in df.columns:
        raise ValueError("CSV 파일에 'section' 컬럼이 없습니다! 컬럼명을 확인해주세요.")
    
    if len(df) != len(embeddings):
        raise ValueError("데이터와 임베딩 개수가 맞지 않습니다!")

    # 2. ChromaDB 클라이언트 설정
    # persist_directory: DB가 저장될 로컬 폴더 경로
    client = chromadb.PersistentClient(path="rag/chroma_db_bge")
    
    # 컬렉션 생성 (이미 있으면 삭제 후 재생성 추천)
    collection_name = "translation_memory"
    try:
        client.delete_collection(name=collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"} # 코사인 유사도 사용
    )

    # 3. 데이터 삽입 (배치 처리)
    batch_size = 50
    total_size = len(df)
    
    print(f"DB 구축 시작 (총 {total_size}건)...")
    
    for i in range(0, total_size, batch_size):
        end = min(i + batch_size, total_size)
        
        # ID 생성 (문자열이어야 함)
        ids = [str(idx) for idx in df.iloc[i:end]["id"].tolist()] # id 컬럼 사용
        # 문서 내용 (원문)
        documents = df.iloc[i:end]["original_sentence"].tolist()

        answers = df.iloc[i:end]["answer_sentence"].tolist()
        sections = df.iloc[i:end]["section"].tolist()
        
        # 메타데이터 (정답 번역)
        metadatas = [
            {"answer": ans, "section": sec} 
            for ans, sec in zip(answers, sections)
        ]
        
        # 임베딩 벡터 (Colab에서 가져온 것)
        embeddings_batch = embeddings[i:end].tolist()
        
        # ChromaDB에 추가 (임베딩 계산 과정 없이 바로 들어감 -> 초고속)
        collection.add(
            ids=ids,
            embeddings=embeddings_batch,
            documents=documents,
            metadatas=metadatas
        )
        print(f"  - {end}/{total_size} 저장 완료")

    print("✅ ChromaDB 구축 완료! ('rag/chroma_db_bge' 폴더 생성됨)")

if __name__ == "__main__":
    build_vector_db()