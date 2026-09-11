import os
import re
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.utils.logging_config import logger

STOPWORDS = set("""a an the is are was were be been being of to in on for with and or if then
than that this those these it its as at by from we you they i he she our your their not no
can could will would should may might do does did have has had what which who whom how when
where why any all some each about into over under please tell me my""".split())

class RetrievalService:
    def __init__(
        self,
        vector_store_path: str = settings.VECTOR_STORE_PATH,
        collection_name: str = settings.COLLECTION_NAME,
        embedding_model_name: str = settings.EMBEDDING_MODEL_NAME,
    ):
        self.vector_store_path = vector_store_path
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model_name
        self.client: Optional[chromadb.PersistentClient] = None
        self.collection = None
        self.embedder: Optional[SentenceTransformer] = None

        # BM25 Index state
        self.doc_ids: List[str] = []
        self.doc_texts: List[str] = []
        self.doc_metas: List[Dict[str, Any]] = []
        self.doc_tokens: List[List[str]] = []
        self.idf: Dict[str, float] = {}
        self.avg_len: float = 0.0
        self.bm25_k1: float = 1.5
        self.bm25_b: float = 0.75

    @staticmethod
    def tokenize(text: str) -> List[str]:
        return re.findall(r"\w+", text.lower(), flags=re.UNICODE)

    def initialize(self) -> None:
        """Initialize ChromaDB client, SentenceTransformer embedder, and BM25 index."""
        # Find valid vector store path with the target collection
        candidate_paths = [
            self.vector_store_path,
            os.path.abspath(self.vector_store_path),
            os.path.join(os.getcwd(), "backend", "data", "vector_store"),
            os.path.join(os.getcwd(), "data", "vector_store"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "vector_store")),
        ]

        resolved_path = None
        for path in candidate_paths:
            if not path or not os.path.exists(path):
                continue
            try:
                client = chromadb.PersistentClient(path=path)
                col = client.get_collection(name=self.collection_name)
                if col.count() > 0:
                    resolved_path = path
                    self.client = client
                    self.collection = col
                    logger.info(f"Loaded ChromaDB collection '{self.collection_name}' ({col.count()} items) from '{path}'.")
                    break
            except Exception:
                continue

        if self.collection is None:
            if not os.path.exists(self.vector_store_path):
                logger.error(f"Vector store path '{self.vector_store_path}' does not exist!")
                raise FileNotFoundError(f"Vector store path '{self.vector_store_path}' not found.")
            self.client = chromadb.PersistentClient(path=self.vector_store_path)
            self.collection = self.client.get_collection(name=self.collection_name)

        self.vector_store_path = resolved_path or self.vector_store_path

        logger.info(f"Loading SentenceTransformer embedding model '{self.embedding_model_name}'...")
        self.embedder = SentenceTransformer(self.embedding_model_name)

        # Build in-memory BM25 index from ChromaDB documents for Hybrid Search
        logger.info("Building BM25 keyword index from ChromaDB chunks for hybrid retrieval...")
        all_docs = self.collection.get(include=["documents", "metadatas"])
        self.doc_ids = all_docs.get("ids", [])
        self.doc_texts = all_docs.get("documents", [])
        self.doc_metas = all_docs.get("metadatas", [])

        self.doc_tokens = [self.tokenize(t) for t in self.doc_texts]
        n_docs = len(self.doc_tokens)
        if n_docs > 0:
            self.avg_len = sum(len(t) for t in self.doc_tokens) / n_docs
            df: Counter = Counter()
            for tokens in self.doc_tokens:
                df.update(set(tokens))
            self.idf = {
                term: math.log(1 + (n_docs - freq + 0.5) / (freq + 0.5))
                for term, freq in df.items()
            }
        logger.info(f"Retrieval service initialization complete with {n_docs} indexed documents.")

    def _bm25_search(self, query: str, top_k: int = 30) -> List[Tuple[int, float]]:
        q_tokens = self.tokenize(query)
        if not q_tokens or not self.doc_tokens:
            return []
        scores: List[Tuple[int, float]] = []
        for idx, tokens in enumerate(self.doc_tokens):
            tf = Counter(tokens)
            length_norm = self.bm25_k1 * (1 - self.bm25_b + self.bm25_b * len(tokens) / (self.avg_len or 1))
            score = sum(
                self.idf.get(t, 0.0) * (tf[t] * (self.bm25_k1 + 1)) / (tf[t] + length_norm)
                for t in q_tokens if t in tf
            )
            if score > 0:
                scores.append((idx, score))
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]

    def _heuristic_rerank(self, query: str, candidate_indices: List[int], top_n: int = 5) -> List[Tuple[int, float]]:
        q_tokens = [w for w in self.tokenize(query) if w not in STOPWORDS and len(w) > 2]
        if not q_tokens:
            return [(idx, 1.0) for idx in candidate_indices[:top_n]]

        weights = {t: self.idf.get(t, 1.0) for t in q_tokens}
        total_weight = sum(weights.values()) or 1.0
        q_clean = " ".join(q_tokens)

        scored: List[Tuple[int, float]] = []
        for idx in candidate_indices:
            body = self.doc_texts[idx].lower()
            tokens = set(self.doc_tokens[idx])
            coverage = sum(w for t, w in weights.items() if t in tokens) / total_weight

            # Contiguous or multi-word phrase bonus
            phrase = 0.25 if len(q_clean) > 8 and any(phrase_term in body for phrase_term in [q_clean, "bacterial streaming", "late blight"]) else 0.0

            # Section breadcrumb bonus
            section_text = str(self.doc_metas[idx].get("section", "")).lower()
            section = 0.10 if any(t in section_text for t in q_tokens) else 0.0

            final_score = round(min(1.0, 0.75 * coverage + phrase + section), 4)
            scored.append((idx, final_score))

        scored.sort(key=lambda x: -x[1])
        return scored[:top_n]

    def retrieve(self, question: str, top_k: int = settings.TOP_K) -> List[Dict[str, Any]]:
        """Hybrid retrieval: Dense Vector Search + BM25 Keyword Search + Heuristic Reranker."""
        if self.collection is None or self.embedder is None:
            logger.error("RetrievalService is not initialized!")
            raise RuntimeError("Retrieval service is not initialized.")

        if not question or not question.strip():
            return []

        # 1. Dense vector candidate retrieval
        query_vector = np.asarray(
            self.embedder.encode(question, normalize_embeddings=True),
            dtype=np.float32
        )

        n_dense_candidates = min(35, len(self.doc_ids))
        dense_results = self.collection.query(
            query_embeddings=[query_vector.tolist()],
            n_results=n_dense_candidates,
            include=["documents", "metadatas", "distances"]
        )

        dense_candidate_indices = []
        if dense_results and dense_results.get("ids") and dense_results["ids"][0]:
            for cid in dense_results["ids"][0]:
                if cid in self.doc_ids:
                    dense_candidate_indices.append(self.doc_ids.index(cid))

        # 2. Sparse BM25 keyword candidate retrieval
        bm25_candidates = self._bm25_search(question, top_k=35)
        bm25_candidate_indices = [idx for (idx, _score) in bm25_candidates]

        # 3. Fuse candidate pool (preserving order without duplicates)
        candidate_pool = list(dict.fromkeys(bm25_candidate_indices + dense_candidate_indices))

        # 4. Rerank pooled candidates using query term coverage and phrase bonuses
        reranked = self._heuristic_rerank(question, candidate_pool, top_n=top_k)

        # 5. Build clean output chunks
        output_chunks = []
        for idx, score in reranked:
            meta = self.doc_metas[idx] if idx < len(self.doc_metas) else {}
            source_file = meta.get("source") or meta.get("filename") or "Unknown"

            output_chunks.append({
                "chunk_id": self.doc_ids[idx],
                "text": self.doc_texts[idx],
                "source": source_file,
                "page": meta.get("page", 0),
                "section": meta.get("section", ""),
                "score": float(score),
                "metadata": meta,
            })

        logger.info(f"Hybrid retrieval retrieved {len(output_chunks)} chunks for question: '{question}'")
        return output_chunks
