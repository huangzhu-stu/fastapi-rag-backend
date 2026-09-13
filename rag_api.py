import os
import faiss
import requests
import json
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="RAG知识库中台API")

DOC_FOLDER = "./docs"
DB_PATH = "./faiss_index.bin"
STORE_PATH = "./texts_store.json"

EMBED_URL = "http://127.0.0.1:11434/api/embeddings"
LLM_URL = "http://127.0.0.1:11434/api/generate"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "qwen:7b"

index = None
doc_texts = []

class ChatRequest(BaseModel):
    query: str
    top_k: int = 2

def get_embedding(text: str):
    resp = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    return np.array(resp.json()["embedding"], dtype=np.float32)

def build_vector_index():
    global index, doc_texts
    doc_texts = []
    for fname in os.listdir(DOC_FOLDER):
        if fname.lower().endswith(".txt"):
            full = os.path.join(DOC_FOLDER, fname)
            with open(full, "r", encoding="utf-8") as f:
                doc_texts.append(f.read())
    emb_list = []
    for txt in doc_texts:
        emb_list.append(get_embedding(txt))
    emb_arr = np.array(emb_list, dtype=np.float32)
    dim = emb_arr.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(emb_arr)
    faiss.write_index(index, DB_PATH)
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(doc_texts, f, ensure_ascii=False)
    return {"dim": dim, "doc_count": len(doc_texts)}

def load_index():
    global index, doc_texts
    if os.path.exists(DB_PATH) and os.path.exists(STORE_PATH):
        index = faiss.read_index(DB_PATH)
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            doc_texts = json.load(f)
        return True
    return False

@app.post("/rag/rebuild", summary="重建知识库")
def rebuild():
    info = build_vector_index()
    return {"code":0, "msg":"知识库重建完成", "data":info}

@app.post("/rag/chat", summary="RAG问答接口")
def chat(req: ChatRequest):
    global index, doc_texts
    if index is None:
        if not load_index():
            return {"code":-1, "msg":"请先调用重建知识库接口"}
    q_emb = get_embedding(req.query).reshape(1,-1)
    _, idx_list = index.search(q_emb, req.top_k)
    hit_docs = [doc_texts[i] for i in idx_list[0]]
    context = "\n=====\n".join(hit_docs)
    prompt = f"""参考下面文档回答用户问题，只依据文档内容回答。
【参考文档】
{context}
【用户问题】
{req.query}
"""
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    }
    resp = requests.post(LLM_URL, json=payload)
    answer = resp.json()["response"]
    return {
        "code":0,
        "query": req.query,
        "retrieve_docs": hit_docs,
        "answer": answer
    }

if __name__ == "__main__":
    if not os.path.exists(DOC_FOLDER):
        os.makedirs(DOC_FOLDER)
    load_index()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)