from typing import List
import hashlib
from sentence_transformers import SentenceTransformer
import numpy as np


class TextEmbedder:
    def __init__(self, model_name: str = "google/embeddinggemma-300m"):
        self.model = SentenceTransformer(model_name, local_files_only=True)
        self.max_length = self.model.max_seq_length

    def _chunk_text(self, text: str, overlap: int = 100) -> List[str]:
        # may warn about token indices sequence length is longer than the specified maximum sequence length for this model , ignore it
        tokens = self.model.tokenizer.encode(text, add_special_tokens=False)
        if len(tokens) <= self.max_length:
            return [text]
        step = self.max_length - overlap
        if step <= 0:
            raise ValueError("overlap must be smaller than max_length")
        chunks: List[str] = []
        for start in range(0, len(tokens), step):
            chunk_tokens = tokens[start:start + self.max_length]
            if not chunk_tokens:
                break
            chunk_text = self.model.tokenizer.decode(
                chunk_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            chunks.append(chunk_text)
        return chunks

    def _encode(self, text: str) -> np.ndarray:
        chunks = self._chunk_text(text)
        if len(chunks) == 1:
            return self.model.encode(chunks[0], normalize_embeddings=True)
        chunk_embeddings = self.model.encode(
            chunks,
            normalize_embeddings=False,
            show_progress_bar=False
        )
        pooled = np.max(chunk_embeddings, axis=0)
        norm = np.linalg.norm(pooled)
        if norm == 0:
            return pooled
        return pooled / norm

    def similarity_matrix(self, texts: List[str]) -> np.ndarray:
        embeddings = np.array([self._encode(text) for text in texts])
        sim = embeddings @ embeddings.T
        return np.clip(sim, -1.0, 1.0)

    def similarity_to_many(self, query: str, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([])
        query_emb = self._encode(query)
        text_embeddings = np.array([self._encode(t) for t in texts])
        scores = text_embeddings @ query_emb
        return np.clip(scores, -1.0, 1.0)

    def get_text_hex_prefix(self, text: str, length: int = 8) -> str:
        md5 = hashlib.md5(text.encode('utf-8'))
        hex_digest = md5.hexdigest()
        return hex_digest[:length]
