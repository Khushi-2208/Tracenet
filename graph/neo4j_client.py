import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from neo4j import GraphDatabase, Driver
    HAS_NEO4J_LIB = True
except ImportError:
    HAS_NEO4J_LIB = False

logger = logging.getLogger(__name__)

class Neo4jClient:
    """
    Neo4j Database Interface for TRACENET Characteristic Graph.
    Manages node creation, Cypher query executions, and schema relationship mapping.
    """
    def __init__(self, uri: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "tracenet_secure_pass")
        self.driver: Optional[Driver] = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """Establishes connection to the Neo4j instance."""
        if not HAS_NEO4J_LIB:
            logger.warning("neo4j library is not installed.")
            self.is_connected = False
            return False
            
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            self.driver.verify_connectivity()
            self.is_connected = True
            logger.info("Successfully connected to Neo4j database.")
            return True
        except Exception as e:
            logger.warning(f"Could not connect to Neo4j at {self.uri}: {e}")
            self.is_connected = False
            return False

    def close(self):
        """Closes the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            self.is_connected = False

    def clear_database(self):
        """Wipes existing database graph data."""
        if not self.is_connected or not self.driver:
            return
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def build_graph_from_dataframe(self, df) -> bool:
        """
        Dynamically ingests DataFrame rows into Neo4j graph nodes and relationships:
        Nodes: Username, PGPKey, Wallet, Domain, Post, Source
        Relationships:
          (Username)-[:USES]->(PGPKey)
          (Username)-[:ASSOCIATED_WITH]->(Wallet)
          (Username)-[:USES]->(Domain)
          (Username)-[:AUTHORED]->(Post)
          (Post)-[:FROM_SOURCE]->(Source)
        """
        if not self.is_connected or not self.driver:
            return False
            
        self.clear_database()
        
        cypher_query = """
        UNWIND $rows AS row
        MERGE (u:Username {name: row.username})
        MERGE (p:PGPKey {key_id: row.pgp_key})
        MERGE (w:Wallet {address: row.wallet_id})
        MERGE (d:Domain {name: row.domain})
        MERGE (s:Source {name: row.source})
        CREATE (post:Post {text: row.cleaned_text, timestamp: row.timestamp})
        
        MERGE (u)-[:USES]->(p)
        MERGE (u)-[:ASSOCIATED_WITH]->(w)
        MERGE (u)-[:USES]->(d)
        MERGE (u)-[:AUTHORED]->(post)
        MERGE (post)-[:FROM_SOURCE]->(s)
        """
        
        rows_data = df.to_dict(orient='records')
        
        try:
            with self.driver.session() as session:
                session.run(cypher_query, rows=rows_data)
            logger.info(f"Ingested {len(rows_data)} records into Neo4j.")
            return True
        except Exception as e:
            logger.error(f"Error populating Neo4j graph: {e}")
            return False

    def query_username_profile(self, username: str) -> Dict[str, Any]:
        """
        Cypher query retrieving all associated PGPs, wallets, domains, posts, and related usernames.
        """
        if not self.is_connected or not self.driver:
            return {}
            
        cypher = """
        MATCH (u:Username {name: $username})
        OPTIONAL MATCH (u)-[:USES]->(p:PGPKey)
        OPTIONAL MATCH (u)-[:ASSOCIATED_WITH]->(w:Wallet)
        OPTIONAL MATCH (u)-[:USES]->(d:Domain)
        OPTIONAL MATCH (u)-[:AUTHORED]->(post:Post)
        OPTIONAL MATCH (related:Username) WHERE related.name <> $username AND (
            (related)-[:USES]->(p) OR
            (related)-[:ASSOCIATED_WITH]->(w) OR
            (related)-[:USES]->(d)
        )
        RETURN 
            u.name AS username,
            collect(DISTINCT p.key_id) AS pgp_keys,
            collect(DISTINCT w.address) AS wallets,
            collect(DISTINCT d.name) AS domains,
            count(DISTINCT post) AS post_count,
            collect(DISTINCT related.name) AS related_usernames
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(cypher, username=username)
                record = result.single()
                if record:
                    return {
                        "username": record["username"],
                        "pgp_keys": record["pgp_keys"],
                        "wallets": record["wallets"],
                        "domains": record["domains"],
                        "post_count": record["post_count"],
                        "related_usernames": record["related_usernames"]
                    }
        except Exception as e:
            logger.error(f"Cypher error querying username {username}: {e}")
            
        return {}
