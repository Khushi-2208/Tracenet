"""
Application State Manager for TRACENET Backend.
Holds processed data, graph, relationships, and model instances in memory.
Singleton pattern shared across all API routes.
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional

from ingestion.csv_processor import load_and_preprocess_csv
from graph.graph_builder import CharacteristicGraph
from ai.stylometry import StylometryAnalyzer
from scoring.confidence import ConfidenceScorer


class AppState:
    """
    Centralized application state for the TRACENET backend.
    Manages the lifecycle of data processing, graph construction,
    AI analysis, and investigation results.
    """

    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.stats: Dict[str, int] = {}
        self.graph: Optional[CharacteristicGraph] = None
        self.relationships: List[Dict[str, Any]] = []
        self.stylometry_meta: Dict[str, Any] = {}
        self.stylometer: Optional[StylometryAnalyzer] = None
        self.is_processed: bool = False

    def initialize_model(self):
        """Load the SentenceTransformer model once at startup."""
        if self.stylometer is None:
            self.stylometer = StylometryAnalyzer()

    def process_csv(self, file_input) -> Dict[str, Any]:
        """
        Full processing pipeline:
        1. Read & validate CSV
        2. Build characteristic graph (NetworkX + Neo4j)
        3. Run AI stylometry analysis
        4. Calculate confidence scores
        """
        # 1. Ingestion & Preprocessing
        df, stats = load_and_preprocess_csv(file_input)
        self.df = df
        self.stats = stats

        # 2. Build Characteristic Graph
        cgraph = CharacteristicGraph()
        cgraph.build_graph(df)
        self.graph = cgraph

        # 3. AI Stylometry & Confidence Scoring
        if self.stylometer is None:
            self.initialize_model()

        scorer = ConfidenceScorer(self.stylometer)
        relationships = scorer.compute_all_pair_scores(df)
        self.relationships = relationships
        self.stylometry_meta = {
            "engine": self.stylometer.embedding_engine.engine_type,
            "usernames_analyzed": stats["unique_usernames"]
        }

        self.is_processed = True

        return {
            "records_processed": stats["records_processed"],
            "unique_usernames": stats["unique_usernames"],
            "unique_pgp_keys": stats["unique_pgp_keys"],
            "unique_wallets": stats["unique_wallets"],
            "unique_domains": stats["unique_domains"],
            "unique_sources": stats["unique_sources"],
            "potential_links": len([r for r in relationships if r["confidence_score"] >= 0.75]),
            "neo4j_active": cgraph.neo4j_active
        }

    def reset(self):
        """Clear all processed data."""
        self.df = None
        self.stats = {}
        self.graph = None
        self.relationships = []
        self.stylometry_meta = {}
        self.is_processed = False

    def get_actor_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Get actor profile from the characteristic graph."""
        if not self.is_processed or not self.graph:
            return None
        return self.graph.get_username_profile(username, self.df)

    def get_actor_graph_data(self, username: str) -> Dict[str, Any]:
        """Get D3-compatible subgraph data for a specific actor."""
        if not self.is_processed or not self.graph:
            return {"nodes": [], "links": []}

        nx_graph = self.graph.nx_graph
        if username not in nx_graph:
            return {"nodes": [], "links": []}

        # BFS to collect 2-hop neighborhood
        subgraph_nodes = set()
        subgraph_nodes.add(username)

        # First hop neighbors
        for neighbor in nx_graph.neighbors(username):
            subgraph_nodes.add(neighbor)
            # Second hop — other users connected via shared entities
            n_type = nx_graph.nodes[neighbor].get("node_type")
            if n_type in ("PGPKey", "Wallet", "Domain"):
                for second_hop in nx_graph.neighbors(neighbor):
                    if nx_graph.nodes[second_hop].get("node_type") == "Username":
                        subgraph_nodes.add(second_hop)
                        # Also add that user's direct entities
                        for third in nx_graph.neighbors(second_hop):
                            t_type = nx_graph.nodes[third].get("node_type")
                            if t_type in ("PGPKey", "Wallet", "Domain"):
                                subgraph_nodes.add(third)

        return self._graph_to_d3(nx_graph.subgraph(subgraph_nodes))

    def get_full_graph_data(self) -> Dict[str, Any]:
        """Get D3-compatible full graph data."""
        if not self.is_processed or not self.graph:
            return {"nodes": [], "links": []}
        return self._graph_to_d3(self.graph.nx_graph)

    def _graph_to_d3(self, nx_graph) -> Dict[str, Any]:
        """Convert a NetworkX graph to D3.js force-directed format."""
        nodes = []
        links = []
        node_set = set()

        for node, data in nx_graph.nodes(data=True):
            if node not in node_set:
                node_set.add(node)
                nodes.append({
                    "id": str(node),
                    "label": str(data.get("label", node)),
                    "type": data.get("node_type", "Unknown"),
                    "title": data.get("title", str(node))
                })

        for u, v, data in nx_graph.edges(data=True):
            links.append({
                "source": str(u),
                "target": str(v),
                "rel_type": data.get("rel_type", "CONNECTED")
            })

        return {"nodes": nodes, "links": links}

    def get_timeline(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get chronological activity timeline, optionally filtered by username."""
        if not self.is_processed or self.df is None:
            return []

        df = self.df.copy()
        if username:
            df = df[df["username"] == username]

        df = df.sort_values("parsed_timestamp", ascending=False)

        timeline = []
        for _, row in df.iterrows():
            timeline.append({
                "timestamp": str(row["parsed_timestamp"]),
                "username": row["username"],
                "domain": row["domain"],
                "source": row["source"],
                "pgp_key": row["pgp_key"],
                "wallet_id": row["wallet_id"],
                "text": row["cleaned_text"][:120] + ("..." if len(row["cleaned_text"]) > 120 else ""),
                "full_text": row["cleaned_text"]
            })

        return timeline

    def search_entities(self, query: str) -> List[Dict[str, str]]:
        """Search across graph entities."""
        if not self.is_processed or not self.graph:
            return []
        return self.graph.search_entities(query)

    def update_relationship(self, username_a: str, username_b: str,
                            status: Optional[str] = None,
                            notes: Optional[str] = None) -> bool:
        """Update investigator review status or notes for a relationship."""
        for rel in self.relationships:
            if ((rel["username_a"] == username_a and rel["username_b"] == username_b) or
                (rel["username_a"] == username_b and rel["username_b"] == username_a)):
                if status is not None:
                    rel["investigator_review_status"] = status
                if notes is not None:
                    rel["review_notes"] = notes
                return True
        return False


# Global singleton instance
app_state = AppState()
