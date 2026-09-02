import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.metrics.pairwise import cosine_similarity
from .embeddings import TextEmbeddingEngine

class StylometryAnalyzer:
    """
    Username Writing-Style Similarity Engine for TRACENET.
    Aggregates user post texts, generates pretrained BERT/RoBERTa embeddings, and computes cosine similarity.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embedding_engine = TextEmbeddingEngine(model_name=model_name)

    def analyze_usernames(self, df: pd.DataFrame) -> Tuple[Dict[Tuple[str, str], float], Dict[str, Any]]:
        """
        Computes pairwise writing-style similarity matrix across unique usernames.
        Returns:
            similarity_pairs: Dict mapping (username_a, username_b) -> writing_similarity score (0.0 to 1.0)
            metadata: Dict containing engine details and notice statement.
        """
        # 1. Group all text posts per username
        user_texts = df.groupby('username')['cleaned_text'].apply(lambda posts: " ".join(posts)).to_dict()
        usernames = list(user_texts.keys())
        
        if len(usernames) < 2:
            return {}, {"engine": self.embedding_engine.engine_type, "usernames_analyzed": len(usernames)}

        # 2. Extract text embeddings
        texts = [user_texts[u] for u in usernames]
        embeddings = self.embedding_engine.get_embeddings(texts)

        # 3. Compute cosine similarity matrix
        sim_matrix = cosine_similarity(embeddings)

        # Normalize matrix values strictly between 0.0 and 1.0
        sim_matrix = np.clip(sim_matrix, 0.0, 1.0)

        similarity_pairs = {}
        for i in range(len(usernames)):
            for j in range(i + 1, len(usernames)):
                u_a = usernames[i]
                u_b = usernames[j]
                score = float(sim_matrix[i, j])
                
                # Store bi-directional key access
                similarity_pairs[(u_a, u_b)] = round(score, 4)
                similarity_pairs[(u_b, u_a)] = round(score, 4)

        metadata = {
            "engine": self.embedding_engine.engine_type,
            "usernames_analyzed": len(usernames),
            "disclaimer": "Prototype stylometric similarity signal (Semantic/Writing structure embedding similarity), not an authorship proof."
        }

        return similarity_pairs, metadata
