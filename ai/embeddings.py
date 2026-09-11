import logging
import numpy as np
from typing import List, Dict

logger = logging.getLogger(__name__)

# Try sentence-transformers first, then transformers/torch, then TF-IDF fallback
HAS_SENTENCE_TRANSFORMERS = False
HAS_TRANSFORMERS = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    pass

if not HAS_SENTENCE_TRANSFORMERS:
    try:
        from transformers import AutoTokenizer, AutoModel
        import torch
        HAS_TRANSFORMERS = True
    except ImportError:
        pass

from sklearn.feature_extraction.text import TfidfVectorizer

class TextEmbeddingEngine:
    """
    BERT/RoBERTa Dense Semantic & Stylometric Vector Extractor for TRACENET.
    Generates text embedding vectors using sentence-transformers or pretrained transformer architectures.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.engine_type = "TF-IDF"
        self._initialize_model()

    def _initialize_model(self):
        """Initializes the best available transformer embedding engine."""
        low_memory = os.getenv("LOW_MEMORY_MODE", "false").lower() in ("true", "1", "yes")

        if not low_memory and HAS_SENTENCE_TRANSFORMERS:
            try:
                logger.info(f"Loading SentenceTransformer model: {self.model_name}...")
                self.model = SentenceTransformer(self.model_name)
                self.engine_type = f"SentenceTransformer ({self.model_name})"
                return
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer: {e}. Falling back to HuggingFace Transformers.")

        if not low_memory and HAS_TRANSFORMERS:
            try:
                model_hf = "bert-base-uncased"
                logger.info(f"Loading HuggingFace model: {model_hf}...")
                self.tokenizer = AutoTokenizer.from_pretrained(model_hf)
                self.model = AutoModel.from_pretrained(model_hf)
                self.engine_type = f"HuggingFace BERT ({model_hf})"
                return
            except Exception as e:
                logger.warning(f"Could not load HuggingFace Transformers: {e}. Falling back to TF-IDF vectorizer.")

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

        if "HuggingFace BERT" in self.engine_type and self.model and self.tokenizer:
            inputs = self.tokenizer(texts, padding=True, truncation=True, max_length=128, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Mean pooling across tokens
                embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
            return embeddings

        # Fallback: Character & word TF-IDF vectorizer
        vectorizer = TfidfVectorizer(ngram_range=(1, 3), analyzer='char_wb', min_df=1)
        tfidf_matrix = vectorizer.fit_transform(texts).toarray()
        return tfidf_matrix
