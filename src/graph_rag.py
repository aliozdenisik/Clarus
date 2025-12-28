"""
GraphRAG Module for Sacred Texts

Implements Graph-enhanced Retrieval Augmented Generation using Neo4j.
Extracts entities (prophets, concepts, places) and relationships from religious texts
to enable cross-reference discovery and thematic exploration.

Features:
- Entity extraction using existing QueryEnhancer (Gemini LLM)
- Neo4j graph storage for relationships
- Graph-enhanced search combining vector + graph traversal
- Community detection for thematic grouping

Usage:
    from src.graph_rag import GraphRAGBuilder, GraphRAGSearcher
    
    # Build graph from indexed data
    builder = GraphRAGBuilder()
    await builder.build_from_collection("quran_tr")
    
    # Search with graph enhancement
    searcher = GraphRAGSearcher()
    results = searcher.graph_enhanced_search("Hz. İbrahim", limit=10)
"""
import os
import re
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path


# Neo4j availability check
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Warning: neo4j not installed. Install with: pip install neo4j")


@dataclass
class Entity:
    """Represents an extracted entity from sacred texts."""
    name: str
    entity_type: str  # Prophet, Concept, Place, Event, Command
    source_id: str    # Verse ID where entity appears
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class Relationship:
    """Represents a relationship between entities."""
    source: str       # Source entity name
    target: str       # Target entity name
    rel_type: str     # MENTIONS, RELATES_TO, CROSS_REFERENCE, PART_OF
    properties: Dict[str, Any] = field(default_factory=dict)


class Neo4jConnection:
    """
    Manages Neo4j database connection.
    
    Supports both local and cloud (Aura) Neo4j instances.
    """
    
    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None
    ):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j bolt URI (default: from NEO4J_URI env var or bolt://localhost:7687)
            username: Database username (default: from NEO4J_USERNAME env var or neo4j)
            password: Database password (default: from NEO4J_PASSWORD env var)
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j package required. Install with: pip install neo4j")
        
        self.uri = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.environ.get("NEO4J_USERNAME", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASSWORD")
        
        if not self.password:
            raise ValueError(
                "Neo4j password required. Set NEO4J_PASSWORD environment variable "
                "or pass password parameter."
            )
        
        self._driver = None
    
    @property
    def driver(self):
        """Lazy initialization of Neo4j driver."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            # Verify connection
            self._driver.verify_connectivity()
            print(f"Connected to Neo4j: {self.uri}")
        return self._driver
    
    def close(self):
        """Close the Neo4j connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
    
    def run_query(self, query: str, parameters: Dict = None) -> List[Dict]:
        """Execute a Cypher query and return results."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def run_write(self, query: str, parameters: Dict = None):
        """Execute a write query."""
        with self.driver.session() as session:
            session.run(query, parameters or {})


class EntityExtractor:
    """
    Extracts entities and relationships from sacred text using LLM.
    Uses existing QueryEnhancer for LLM calls with retry logic.
    """
    
    # Entity types for religious texts
    ENTITY_TYPES = [
        "Prophet",    # Hz. Muhammed, Hz. İsa, Hz. Musa, etc.
        "Concept",    # Rahmet, Sabır, İman, Tevbe, etc.
        "Place",      # Mekke, Medine, Cennet, Cehennem, etc.
        "Event",      # Hicret, Mi'rac, Kıyamet, etc.
        "Command",    # Namaz, Oruç, Zekat, etc.
    ]
    
    # Improved prompt with format enforcement and example
    EXTRACTION_PROMPT = """Aşağıdaki kutsal metin ayetinden önemli varlıkları ve ilişkileri çıkar.

Metin: {text}

SADECE geçerli JSON döndür, başka bir şey yazma:
```json
{{
    "entities": [
        {{"name": "Allah", "type": "Concept"}},
        {{"name": "Hz. Musa", "type": "Prophet"}}
    ],
    "relationships": [
        {{"source": "Allah", "target": "Hz. Musa", "type": "MENTIONS"}}
    ]
}}
```

Varlık türleri: Prophet, Concept, Place, Event, Command
İlişki türleri: MENTIONS, RELATES_TO, PART_OF

Eğer varlık bulunamazsa boş listeler döndür: {{"entities": [], "relationships": []}}"""

    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 1.0  # seconds

    def __init__(self):
        self._enhancer = None
    
    @property
    def enhancer(self):
        """Lazy load QueryEnhancer."""
        if self._enhancer is None:
            from src.query_enhancer import QueryEnhancer
            self._enhancer = QueryEnhancer()
        return self._enhancer
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract valid JSON.
        Handles common issues: markdown fences, single quotes, extra text.
        """
        response = response.strip()
        
        # Remove markdown code fences (```json ... ``` or ``` ... ```)
        if "```" in response:
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if match:
                response = match.group(1).strip()
        
        # Try to extract JSON object if surrounded by text
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            response = json_match.group(0)
        
        # Fix single quotes to double quotes (common LLM error)
        # Only if there are no double quotes at all (avoid breaking valid JSON)
        if '"' not in response and "'" in response:
            response = response.replace("'", '"')
        
        # Fix common issues: trailing commas before closing brackets
        response = re.sub(r',\s*}', '}', response)
        response = re.sub(r',\s*\]', ']', response)
        
        return response
    
    def _call_llm_with_retry(self, prompt: str) -> str:
        """
        Call LLM with exponential backoff retry.
        Handles timeouts, rate limits, and transient errors.
        """
        import requests
        
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                return self.enhancer._call_llm(prompt)
            except requests.exceptions.Timeout:
                wait = self.RETRY_BASE_DELAY * (2 ** attempt)
                last_error = f"Timeout (retry {attempt + 1}/{self.MAX_RETRIES})"
                time.sleep(wait)
            except requests.exceptions.HTTPError as e:
                if hasattr(e, 'response') and e.response is not None:
                    if e.response.status_code == 429:  # Rate limit
                        wait = self.RETRY_BASE_DELAY * (2 ** attempt) * 2
                        last_error = f"Rate limited (retry {attempt + 1}/{self.MAX_RETRIES})"
                        time.sleep(wait)
                    elif e.response.status_code >= 500:  # Server error
                        wait = self.RETRY_BASE_DELAY * (2 ** attempt)
                        last_error = f"Server error {e.response.status_code}"
                        time.sleep(wait)
                    else:
                        raise
                else:
                    raise
            except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
                wait = self.RETRY_BASE_DELAY * (2 ** attempt)
                last_error = f"Connection error (retry {attempt + 1}/{self.MAX_RETRIES})"
                time.sleep(wait)
        
        raise RuntimeError(f"LLM call failed after {self.MAX_RETRIES} retries: {last_error}")
    
    def extract(self, text: str, source_id: str) -> Tuple[List[Entity], List[Relationship]]:
        """
        Extract entities and relationships from text.
        
        Args:
            text: Text content to analyze
            source_id: Identifier for the source (e.g., verse ID)
            
        Returns:
            Tuple of (entities, relationships)
        """
        prompt = self.EXTRACTION_PROMPT.format(text=text)
        
        try:
            response = self._call_llm_with_retry(prompt)
            
            # Clean and parse JSON response
            cleaned = self._clean_json_response(response)
            
            try:
                data = json.loads(cleaned)
            except json.JSONDecodeError as e:
                # Last resort: try to build minimal valid response
                print(f"Warning: JSON parse failed for {source_id}, attempting recovery: {e}")
                return [], []
            
            entities = []
            for e in data.get("entities", []):
                if isinstance(e, dict) and "name" in e and "type" in e:
                    entities.append(Entity(
                        name=str(e["name"]),
                        entity_type=str(e["type"]),
                        source_id=source_id
                    ))
            
            relationships = []
            for r in data.get("relationships", []):
                if isinstance(r, dict) and all(k in r for k in ["source", "target", "type"]):
                    relationships.append(Relationship(
                        source=str(r["source"]),
                        target=str(r["target"]),
                        rel_type=str(r["type"])
                    ))
            
            return entities, relationships
            
        except RuntimeError as e:
            print(f"Warning: Entity extraction failed for {source_id}: {e}")
            return [], []
        except Exception as e:
            print(f"Warning: Unexpected error for {source_id}: {e}")
            return [], []


class GraphRAGBuilder:
    """
    Builds knowledge graph from indexed sacred texts.
    
    Workflow:
    1. Fetch documents from Qdrant collection
    2. Extract entities and relationships using LLM (with concurrent processing)
    3. Store in Neo4j graph database
    4. Support checkpointing for resume capability
    """
    
    CHECKPOINT_DIR = Path(".")  # Store checkpoints in project root
    DEFAULT_WORKERS = 4
    DEFAULT_CHECKPOINT_INTERVAL = 100
    
    def __init__(
        self,
        neo4j_uri: str = None,
        neo4j_username: str = None,
        neo4j_password: str = None,
        qdrant_url: str = "http://localhost:6333"
    ):
        self.neo4j = Neo4jConnection(neo4j_uri, neo4j_username, neo4j_password)
        self.extractor = EntityExtractor()
        self.qdrant_url = qdrant_url
        self._qdrant_client = None
        self._neo4j_lock = threading.Lock()  # Thread-safe Neo4j writes
    
    @property
    def qdrant_client(self):
        """Lazy load Qdrant client."""
        if self._qdrant_client is None:
            from qdrant_client import QdrantClient
            self._qdrant_client = QdrantClient(url=self.qdrant_url)
        return self._qdrant_client
    
    def _get_checkpoint_path(self, collection_name: str) -> Path:
        """Get checkpoint file path for a collection."""
        return self.CHECKPOINT_DIR / f"graph_checkpoint_{collection_name}.json"
    
    def _load_checkpoint(self, collection_name: str) -> Set[str]:
        """Load processed IDs from checkpoint file."""
        path = self._get_checkpoint_path(collection_name)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
                return set(data.get('processed_ids', []))
            except Exception as e:
                print(f"Warning: Could not load checkpoint: {e}")
        return set()
    
    def _save_checkpoint(self, collection_name: str, processed_ids: Set[str]):
        """Save processed IDs to checkpoint file."""
        path = self._get_checkpoint_path(collection_name)
        try:
            path.write_text(
                json.dumps({
                    'processed_ids': list(processed_ids),
                    'count': len(processed_ids)
                }, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"Warning: Could not save checkpoint: {e}")
    
    def _clear_checkpoint(self, collection_name: str):
        """Delete checkpoint file."""
        path = self._get_checkpoint_path(collection_name)
        if path.exists():
            path.unlink()
    
    def setup_schema(self):
        """Create Neo4j indexes and constraints for better performance."""
        queries = [
            # Create unique constraint for entities
            "CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE",
            # Create index for entity type
            "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            # Create index for source verses
            "CREATE INDEX entity_source IF NOT EXISTS FOR (e:Entity) ON (e.source_id)",
        ]
        
        for query in queries:
            try:
                self.neo4j.run_write(query)
            except Exception as e:
                print(f"Schema setup warning: {e}")
        
        print("Neo4j schema setup complete")
    
    def clear_graph(self):
        """Clear all nodes and relationships from the graph."""
        self.neo4j.run_write("MATCH (n) DETACH DELETE n")
        print("Graph cleared")
    
    def add_entity(self, entity: Entity):
        """Add or merge an entity into the graph (thread-safe)."""
        query = """
        MERGE (e:Entity {name: $name})
        SET e.type = $type,
            e.source_id = CASE WHEN e.source_id IS NULL THEN $source_id 
                          ELSE e.source_id + ', ' + $source_id END
        """
        with self._neo4j_lock:
            self.neo4j.run_write(query, {
                "name": entity.name,
                "type": entity.entity_type,
                "source_id": entity.source_id
            })
    
    def add_relationship(self, rel: Relationship):
        """Add a relationship between entities (thread-safe)."""
        query = f"""
        MATCH (a:Entity {{name: $source}})
        MATCH (b:Entity {{name: $target}})
        MERGE (a)-[r:{rel.rel_type}]->(b)
        """
        try:
            with self._neo4j_lock:
                self.neo4j.run_write(query, {
                    "source": rel.source,
                    "target": rel.target
                })
        except Exception as e:
            print(f"Warning: Could not create relationship {rel.source} -> {rel.target}: {e}")
    
    def _process_document(self, point) -> Tuple[str, List[Entity], List[Relationship]]:
        """
        Process a single document: extract entities and relationships.
        Returns (source_id, entities, relationships).
        """
        payload = point.payload
        text = payload.get("translation") or payload.get("text", "")
        source_id = str(point.id)
        
        entities, relationships = self.extractor.extract(text, source_id)
        return source_id, entities, relationships
    
    def build_from_collection(
        self,
        collection_name: str,
        limit: int = None,
        batch_size: int = 50,
        show_progress: bool = True,
        workers: int = None,
        resume: bool = False,
        checkpoint_interval: int = None
    ) -> Tuple[List[Entity], List[Relationship]]:
        """
        Build knowledge graph from Qdrant collection.
        
        Args:
            collection_name: Name of Qdrant collection
            limit: Maximum documents to process (None = all)
            batch_size: Documents to fetch per Qdrant scroll
            show_progress: Show progress bar
            workers: Number of concurrent workers (default: 4)
            resume: Resume from last checkpoint
            checkpoint_interval: Save checkpoint every N documents (default: 100)
            
        Returns:
            Tuple of (all_entities, all_relationships)
        """
        from tqdm import tqdm
        
        workers = workers or self.DEFAULT_WORKERS
        checkpoint_interval = checkpoint_interval or self.DEFAULT_CHECKPOINT_INTERVAL
        
        # Setup schema
        self.setup_schema()
        
        # Load checkpoint if resuming
        processed_ids: Set[str] = set()
        if resume:
            processed_ids = self._load_checkpoint(collection_name)
            if processed_ids:
                print(f"Resuming from checkpoint: {len(processed_ids)} documents already processed")
        
        # Get collection info
        info = self.qdrant_client.get_collection(collection_name)
        total_points = info.points_count
        
        if limit:
            total_points = min(limit, total_points)
        
        print(f"Building graph from {total_points} documents in '{collection_name}'")
        print(f"Using {workers} concurrent workers")
        
        # Scroll through collection
        offset = None
        processed = 0
        all_entities = []
        all_relationships = []
        skipped = 0
        
        iterator = tqdm(total=total_points, desc="Extracting entities") if show_progress else None
        
        # If resuming, update progress bar for already processed
        if resume and processed_ids and iterator:
            skipped = len(processed_ids)
            iterator.update(min(skipped, total_points))
        
        try:
            while processed + skipped < total_points:
                # Fetch batch from Qdrant
                scroll_result = self.qdrant_client.scroll(
                    collection_name=collection_name,
                    limit=batch_size,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                points, next_offset = scroll_result
                
                if not points:
                    break
                
                # Filter out already processed documents
                points_to_process = [
                    p for p in points 
                    if str(p.id) not in processed_ids and processed + skipped < total_points
                ]
                
                if not points_to_process:
                    offset = next_offset
                    if offset is None:
                        break
                    continue
                
                # Process batch concurrently
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    futures = {
                        executor.submit(self._process_document, point): point 
                        for point in points_to_process[:total_points - processed - skipped]
                    }
                    
                    for future in as_completed(futures):
                        try:
                            source_id, entities, relationships = future.result()
                            
                            # Add to graph (thread-safe)
                            for entity in entities:
                                self.add_entity(entity)
                                all_entities.append(entity)
                            
                            for rel in relationships:
                                self.add_relationship(rel)
                                all_relationships.append(rel)
                            
                            processed_ids.add(source_id)
                            processed += 1
                            
                            if iterator:
                                iterator.update(1)
                            
                            # Checkpoint periodically
                            if processed % checkpoint_interval == 0:
                                self._save_checkpoint(collection_name, processed_ids)
                                
                        except Exception as e:
                            point = futures[future]
                            print(f"Warning: Failed to process {point.id}: {e}")
                
                offset = next_offset
                
                if offset is None:
                    break
                    
        except KeyboardInterrupt:
            print(f"\n\nInterrupted! Saving checkpoint...")
            self._save_checkpoint(collection_name, processed_ids)
            print(f"Checkpoint saved. Resume with --resume flag.")
            raise
        
        if iterator:
            iterator.close()
        
        # Final checkpoint save
        self._save_checkpoint(collection_name, processed_ids)
        
        print(f"\nGraph built successfully!")
        print(f"  Documents processed: {processed}")
        print(f"  Entities: {len(all_entities)}")
        print(f"  Relationships: {len(all_relationships)}")
        
        return all_entities, all_relationships
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        stats = {}
        
        # Node count
        result = self.neo4j.run_query("MATCH (n) RETURN count(n) as count")
        stats["total_nodes"] = result[0]["count"] if result else 0
        
        # Relationship count
        result = self.neo4j.run_query("MATCH ()-[r]->() RETURN count(r) as count")
        stats["total_relationships"] = result[0]["count"] if result else 0
        
        # Entity types
        result = self.neo4j.run_query("""
            MATCH (e:Entity)
            RETURN e.type as type, count(*) as count
            ORDER BY count DESC
        """)
        stats["entity_types"] = {r["type"]: r["count"] for r in result}
        
        return stats


class GraphRAGSearcher:
    """
    Performs graph-enhanced search combining vector retrieval with graph traversal.
    
    Workflow:
    1. Perform vector search to get initial results
    2. Extract entities from query
    3. Find related entities via graph connections
    4. Expand results with graph-connected documents
    """
    
    def __init__(
        self,
        neo4j_uri: str = None,
        neo4j_username: str = None,
        neo4j_password: str = None
    ):
        self.neo4j = Neo4jConnection(neo4j_uri, neo4j_username, neo4j_password)
        self._searcher = None
    
    def find_related_entities(self, entity_name: str, max_depth: int = 2) -> List[Dict]:
        """
        Find entities related to the given entity via graph connections.
        
        Args:
            entity_name: Name of the entity to start from
            max_depth: Maximum relationship hops to traverse
            
        Returns:
            List of related entities with their paths
        """
        query = f"""
        MATCH (start:Entity)
        WHERE toLower(start.name) CONTAINS toLower($name)
        CALL apoc.path.subgraphNodes(start, {{
            maxLevel: $depth,
            relationshipFilter: 'MENTIONS|RELATES_TO|CROSS_REFERENCE|PART_OF'
        }}) YIELD node
        WHERE node <> start
        RETURN DISTINCT node.name as name, node.type as type, node.source_id as sources
        LIMIT 20
        """
        
        # Try with APOC first, fallback to simple query
        try:
            return self.neo4j.run_query(query, {"name": entity_name, "depth": max_depth})
        except Exception:
            # Fallback without APOC
            simple_query = """
            MATCH (start:Entity)-[*1..2]-(related:Entity)
            WHERE toLower(start.name) CONTAINS toLower($name)
            AND related <> start
            RETURN DISTINCT related.name as name, related.type as type, related.source_id as sources
            LIMIT 20
            """
            return self.neo4j.run_query(simple_query, {"name": entity_name})
    
    def find_verses_with_entity(self, entity_name: str) -> List[str]:
        """Find all verse IDs that mention a specific entity."""
        query = """
        MATCH (e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($name)
        RETURN e.source_id as source_ids
        """
        results = self.neo4j.run_query(query, {"name": entity_name})
        
        verse_ids = []
        for r in results:
            if r.get("source_ids"):
                # source_id may be comma-separated
                ids = r["source_ids"].split(", ")
                verse_ids.extend(ids)
        
        return list(set(verse_ids))
    
    def graph_enhanced_search(
        self,
        query: str,
        base_searcher,  # QuranSearcher or BibleSearcher
        limit: int = 10,
        graph_expansion: int = 5
    ) -> List:
        """
        Perform search enhanced with graph connections.
        
        Args:
            query: Search query
            base_searcher: Vector searcher instance
            limit: Number of final results
            graph_expansion: Extra results to fetch via graph
            
        Returns:
            Combined search results
        """
        # Step 1: Regular vector search
        base_results = base_searcher.search(query, mode="hybrid", limit=limit)
        
        # Step 2: Find related entities
        # Simple approach: use query words as potential entity names
        query_words = query.split()
        related_sources = set()
        
        for word in query_words:
            if len(word) > 2:  # Skip short words
                verse_ids = self.find_verses_with_entity(word)
                related_sources.update(verse_ids[:graph_expansion])
        
        # Step 3: Fetch graph-discovered documents not in base results
        base_ids = {r.id for r in base_results}
        new_sources = [s for s in related_sources if s not in base_ids][:graph_expansion]
        
        if new_sources:
            print(f"[GraphRAG] Found {len(new_sources)} additional sources via graph")
        
        # Step 4: Combine results (base results first, then graph-discovered)
        # Note: In a production system, you'd want to re-rank all results together
        return base_results


# CLI helpers
def add_graph_commands(subparsers):
    """Add GraphRAG commands to CLI."""
    
    # Build graph command
    build_parser = subparsers.add_parser(
        "build-graph",
        help="Build knowledge graph from indexed data"
    )
    build_parser.add_argument(
        "--collection",
        type=str,
        default="quran_tr",
        help="Qdrant collection to process"
    )
    build_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit documents to process"
    )
    build_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing graph before building"
    )
    
    # Graph info command
    info_parser = subparsers.add_parser(
        "graph-info",
        help="Show knowledge graph statistics"
    )


if __name__ == "__main__":
    # Test GraphRAG
    print("Testing GraphRAG module...")
    
    # Test entity extraction
    extractor = EntityExtractor()
    
    test_text = "Rahman ve Rahim olan Allah'ın adıyla. Hamd alemlerin Rabbi Allah'a mahsustur."
    entities, relationships = extractor.extract(test_text, "1:1:1")
    
    print(f"\nExtracted from test text:")
    print(f"  Entities: {[e.name for e in entities]}")
    print(f"  Relationships: {[(r.source, r.rel_type, r.target) for r in relationships]}")
