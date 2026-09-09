from pathlib import Path
import time
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
ROOT=Path(__file__).resolve().parents[1]; GUIDE=ROOT/"data/mrna_safety_guidelines.txt"; DB=ROOT/"outputs/chroma_db"; COLLECTION="mrna_safety_guidelines"; MODEL="all-MiniLM-L6-v2"
def load_chunks():
 text=GUIDE.read_text(encoding="utf-8"); return RecursiveCharacterTextSplitter(chunk_size=1800,chunk_overlap=300,separators=["\n\n","\n",". "," "]).split_text(text)
def build_index():
 chunks=load_chunks(); model=SentenceTransformer(MODEL); client=chromadb.PersistentClient(path=str(DB));
 try: client.delete_collection(COLLECTION)
 except Exception: pass
 col=client.get_or_create_collection(COLLECTION); col.add(ids=[f"chunk-{i}" for i in range(len(chunks))],documents=chunks,embeddings=model.encode(chunks).tolist()); return len(chunks)
def query_guidelines(question,k=3):
 start=time.perf_counter(); col=chromadb.PersistentClient(path=str(DB)).get_collection(COLLECTION); model=SentenceTransformer(MODEL); r=col.query(query_embeddings=model.encode([question]).tolist(),n_results=k); return {"question":question,"chunks":r["documents"][0],"latency_seconds":time.perf_counter()-start}
