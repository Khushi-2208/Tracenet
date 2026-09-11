import os
import logging
import numpy as np
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

from sklearn.feature_extraction.text import TfidfVectorizer

class TextEmbeddingEngine:
    """
    BERT/RoBERTa Dense Semantic & Stylometric Vector Extractor for TRACENET.
    Generates text embedding vectors using sentence-transformers, pretrained transformer architectures,
    or a lightweight TF-IDF vectorizer for low-memory environments (e.g. Render free tier).
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.torch_module = None
        self.engine_type = "TF-IDF"
        self._initialize_model()

    def _initialize_model(self):
        """Initializes the embedding engine based on environment memory constraints."""
        # Default LOW_MEMORY_MODE to true if on cloud or explicitly set
        low_memory_env = os.getenv("LOW_MEMORY_MODE", "true").lower() in ("true", "1", "yes")

        if not low_memory_env:
            # 1. Try sentence-transformers (Lazy Import to prevent pre-loading heavy PyTorch into RAM)
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer model: {self.model_name}...")
                self.model = SentenceTransformer(self.model_name)
                self.engine_type = f"SentenceTransformer ({self.model_name})"
                return
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer: {e}")

            # 2. Try transformers + torch
            try:
                from transformers import AutoTokenizer, AutoModel
                import torch
                self.torch_module = torch
                model_hf = "bert-base-uncased"
                logger.info(f"Loading HuggingFace model: {model_hf}...")
                self.tokenizer = AutoTokenizer.from_pretrained(model_hf)
                self.model = AutoModel.from_pretrained(model_hf)
                self.engine_type = f"HuggingFace BERT ({model_hf})"
                return
            except Exception as e:
                logger.warning(f"Could not load HuggingFace Transformers: {e}")

        # 3. Low-Memory Fallback: Character & word TF-IDF vectorizer (< 50MB RAM)
        logger.info("Using TF-IDF Stylometric Vectorizer (Low Memory Mode).")
        self.engine_type = "TF-IDF Vectorizer (Low Memory Mode)"

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Calculates dense vector embeddings for a list of text strings.
        Returns:
            np.ndarray of shape (N, embedding_dim)
        """
        if not texts:
            return np.array([])

        if "SentenceTransformer" in self.engine_type and self.model:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings

        if "HuggingFace BERT" in self.engine_type and self.model and self.tokenizer and self.torch_module:
            torch = self.torch_module
            inputs = self.tokenizer(texts, padding=True, truncation=True, max_length=128, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
            return embeddings

        # Fallback: Character & word TF-IDF vectorizer
        vectorizer = TfidfVectorizer(ngram_range=(1, 3), analyzer='char_wb', min_df=1)
        tfidf_matrix = vectorizer.fit_transform(texts).toarray()
        return tfidf_matrix
