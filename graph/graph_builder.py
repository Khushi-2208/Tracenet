import networkx as nx
import pandas as pd
from typing import Dict, List, Any, Tuple
from .neo4j_client import Neo4jClient

class CharacteristicGraph:
    """
    Characteristic Graph Generator and Relationship Engine for TRACENET.
    Maintains both Neo4j Cypher storage and local NetworkX graph graph for visualization.
    """
    def __init__(self):
        self.neo4j_client = Neo4jClient()
        self.neo4j_active = self.neo4j_client.connect()
        self.nx_graph = nx.Graph()

    def build_graph(self, df: pd.DataFrame) -> bool:
        """
        Populates both NetworkX graph and Neo4j database (if available).
        """
        # Clear local graph
        self.nx_graph.clear()
        
        # 1. Push to Neo4j if active
        if self.neo4j_active:
            self.neo4j_client.build_graph_from_dataframe(df)

        # 2. Build local NetworkX graph
        for idx, row in df.iterrows():
            u = row['username']
            p = row['pgp_key']
            w = row['wallet_id']
            d = row['domain']
            s = row['source']
            post_id = f"Post_{idx+1}"

            # Add Nodes with Type attributes
            self.nx_graph.add_node(u, node_type="Username", label=u, title=f"Username: {u}")
            self.nx_graph.add_node(p, node_type="PGPKey", label=p, title=f"PGP Key: {p}")
            self.nx_graph.add_node(w, node_type="Wallet", label=w, title=f"Wallet: {w}")
            self.nx_graph.add_node(d, node_type="Domain", label=d, title=f"Domain: {d}")
            self.nx_graph.add_node(s, node_type="Source", label=s, title=f"Source: {s}")

            # Add Edges
            self.nx_graph.add_edge(u, p, rel_type="USES")
            self.nx_graph.add_edge(u, w, rel_type="ASSOCIATED_WITH")
            self.nx_graph.add_edge(u, d, rel_type="USES")
            self.nx_graph.add_edge(u, post_id, rel_type="AUTHORED")
            self.nx_graph.add_edge(post_id, s, rel_type="FROM_SOURCE")
            
            # Label post node
            self.nx_graph.add_node(post_id, node_type="Post", label=f"Post #{idx+1}", title=row['cleaned_text'][:50] + "...")

        return True

    def get_username_profile(self, username: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Queries graph for a specified username to extract associated PGPs, Wallets, Domains, Posts, and Linked Personas.
        """
        # Try Neo4j first
        if self.neo4j_active:
            neo4j_profile = self.neo4j_client.query_username_profile(username)
            if neo4j_profile and neo4j_profile.get("username"):
                # Append user posts from df
                user_posts = df[df['username'] == username]['cleaned_text'].tolist()
                neo4j_profile["posts"] = user_posts
                return neo4j_profile

        # NetworkX fallback
        if username not in self.nx_graph:
            return {}

        pgps = []
        wallets = []
        domains = []
        related_users = set()

        for neighbor in self.nx_graph.neighbors(username):
            ntype = self.nx_graph.nodes[neighbor].get("node_type")
            if ntype == "PGPKey":
                pgps.append(neighbor)
            elif ntype == "Wallet":
                wallets.append(neighbor)
            elif ntype == "Domain":
                domains.append(neighbor)

        # Find connected usernames sharing PGPs, Wallets, or Domains
        shared_entities = pgps + wallets + domains
        for entity in shared_entities:
            for connected_node in self.nx_graph.neighbors(entity):
                if connected_node != username and self.nx_graph.nodes[connected_node].get("node_type") == "Username":
                    related_users.add(connected_node)

        user_posts = df[df['username'] == username]['cleaned_text'].tolist()

        return {
            "username": username,
            "pgp_keys": list(set(pgps)),
            "wallets": list(set(wallets)),
            "domains": list(set(domains)),
            "post_count": len(user_posts),
            "posts": user_posts,
            "related_usernames": list(related_users)
        }

    def search_entities(self, query: str) -> List[Dict[str, str]]:
        """
        Searches graph nodes matching a query string across usernames, wallets, PGPs, and domains.
        """
        results = []
        query_lower = query.lower().strip()
        if not query_lower:
            return results

        for node, data in self.nx_graph.nodes(data=True):
            if query_lower in str(node).lower():
                results.append({
                    "name": node,
                    "type": data.get("node_type", "Unknown")
                })
        return results
