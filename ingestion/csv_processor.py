import pandas as pd
import numpy as np
import re
from typing import Dict, Tuple, Any

REQUIRED_COLUMNS = ['username', 'pgp_key', 'wallet_id', 'domain', 'text', 'timestamp', 'source']

class CSVProcessor:
    """
    Data Extraction and Preprocessing Module for TRACENET.
    Validates, cleans, normalizes, and summarizes CSV cyber threat intelligence input.
    """
    
    def __init__(self, file_path_or_buffer: Any):
        self.raw_data = file_path_or_buffer
        self.df = None
        self.stats = {}

    def process() -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Executes complete ingestion pipeline.
        Returns:
            df: Cleaned and normalized DataFrame.
            stats: Summary metrics dictionary.
        """
        # 1. Load CSV
        if isinstance(self.raw_data, str):
            df = pd.read_csv(self.raw_data)
        else:
            df = pd.read_csv(self.raw_data)
            
        # 2. Validate columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"CSV is missing required column(s): {', '.join(missing_cols)}")
            
        # 3. Drop completely empty or invalid records
        df = df.dropna(subset=['username', 'text']).copy()
        
        # 4. Fill missing non-critical fields with defaults
        df['pgp_key'] = df['pgp_key'].fillna('UNKNOWN_PGP')
        df['wallet_id'] = df['wallet_id'].fillna('UNKNOWN_WALLET')
        df['domain'] = df['domain'].fillna('unknown.onion')
        df['source'] = df['source'].fillna('unknown_source')
        df['timestamp'] = df['timestamp'].fillna('2026-01-01T00:00:00')

        # 5. Normalization
        df['username'] = df['username'].astype(str).str.strip()
        df['pgp_key'] = df['pgp_key'].astype(str).str.strip().str.upper()
        df['wallet_id'] = df['wallet_id'].astype(str).str.strip()
        df['domain'] = df['domain'].astype(str).str.strip().str.lower()
        df['source'] = df['source'].astype(str).str.strip().str.lower()
        
        # Clean text: remove excessive whitespace, keep original case for stylometry analysis
        df['cleaned_text'] = df['text'].astype(str).apply(self._clean_text)
        
        # Parse timestamp safely
        df['parsed_timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['parsed_timestamp'] = df['parsed_timestamp'].fillna(pd.Timestamp('2026-01-01'))

        self.df = df
        
        # 6. Compute statistics summary
        self.stats = {
            "records_processed": len(df),
            "unique_usernames": int(df['username'].nunique()),
            "unique_pgp_keys": int(df['pgp_key'].nunique()),
            "unique_wallets": int(df['wallet_id'].nunique()),
            "unique_domains": int(df['domain'].nunique()),
            "unique_sources": int(df['source'].nunique())
        }
        
        return self.df, self.stats

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Cleans text while preserving structural signals useful for stylometric comparison.
        """
        if not text or pd.isna(text):
            return ""
        # Normalize multiple spaces/tabs into a single space
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()


def load_and_preprocess_csv(file_input: Any) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Helper function to run CSV preprocessing directly."""
    processor = CSVProcessor(file_input)
    return processor.process()
