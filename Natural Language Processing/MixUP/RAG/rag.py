# build_db_local.py
import pandas as pd
import numpy as np
import chromadb
import os

def build_vector_db():
    # 1. 파일 로드
    print("데이터 로딩 중...")
    df = pd.read_csv("data/train_dataset.csv")
    embeddings = np.load("rag/embeddings.npy") 

    if "section" not in df.columns:
        raise ValueError("CSV 파일에 'section' 컬럼이 없습니다! 컬럼명을 확인해주세요.")
    
    if len(df) != len(embeddings):
        raise ValueError("데이터와 임베딩 개수가 맞지 않습니다!")

    # 2. ChromaDB 클라이언트 설정
    client = chromadb.PersistentClient(path="rag/chroma_db_bge")
    
    collection_name = "translation_memory"
    try:
        client.delete_collection(name=collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"} 
    )

    # 3. 데이터 삽입 (배치 처리)
    batch_size = 50
    total_size = len(df)
    
    print(f"DB 구축 시작 (총 {total_size}건)...")
    
    for i in range(0, total_size, batch_size):
        end = min(i + batch_size, total_size)
        
        ids = [str(idx) for idx in df.iloc[i:end]["id"].tolist()] 
        documents = df.iloc[i:end]["original_sentence"].tolist()

        answers = df.iloc[i:end]["answer_sentence"].tolist()
        sections = df.iloc[i:end]["section"].tolist()
        
        metadatas = [
            {"answer": ans, "section": sec} 
            for ans, sec in zip(answers, sections)
        ]
        
        embeddings_batch = embeddings[i:end].tolist()
        
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