"""
Vector Memory System
Uses ChromaDB for semantic search of security incidents and prevention rules
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available. Install with: pip install chromadb")


class VectorMemory:
    """Vector-based memory system for semantic search of security patterns"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize vector memory
        
        Args:
            config: Vector memory configuration
        """
        self.config = config
        self.storage_path = Path(config.get('storage_path', './models/vector_memory'))
        self.collection_name = config.get('collection_name', 'security_incidents')
        self.enabled = config.get('enabled', True) and CHROMADB_AVAILABLE
        
        if not self.enabled:
            logger.warning("Vector memory disabled or ChromaDB not available")
            self.client = None
            self.collection = None
            return
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self._init_client()
    
    def _init_client(self):
        """Initialize ChromaDB client and collection"""
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.storage_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Security incident patterns and prevention rules"}
            )
            
            logger.info(f"Vector memory initialized with {self.collection.count()} entries")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            self.enabled = False
            self.client = None
            self.collection = None
    
    def add_incident_memory(self, incident: Dict[str, Any], memory_entry: Dict[str, Any]):
        """
        Add incident and its memory to vector store
        
        Args:
            incident: Incident data
            memory_entry: Memory entry with prevention rules
        """
        if not self.enabled:
            return
        
        try:
            incident_id = incident.get('incident_id', f"INC-{datetime.now().timestamp()}")
            
            # Create searchable text from incident and memory
            searchable_text = self._create_searchable_text(incident, memory_entry)
            
            # Create metadata
            metadata = {
                'incident_id': incident_id,
                'incident_pattern': memory_entry.get('incident_pattern', ''),
                'severity': incident.get('severity', 'medium'),
                'severity_level': incident.get('severity_level', 3),
                'timestamp': datetime.now().isoformat(),
                'finding_types': json.dumps(self._extract_finding_types(incident)),
                'affected_repos': json.dumps(incident.get('affected_repos', [])),
                'memory_type': memory_entry.get('memory_type', 'security_prevention_rule')
            }
            
            # Store full data as document
            document = json.dumps({
                'incident': incident,
                'memory': memory_entry
            })
            
            # Add to collection
            self.collection.add(
                ids=[incident_id],
                documents=[searchable_text],
                metadatas=[metadata]
            )
            
            logger.info(f"Added incident {incident_id} to vector memory")
        except Exception as e:
            logger.error(f"Failed to add incident to vector memory: {str(e)}")
    
    def search_similar_incidents(self, 
                                 incident: Dict[str, Any], 
                                 n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar past incidents
        
        Args:
            incident: Current incident to find similar patterns for
            n_results: Number of results to return
            
        Returns:
            List of similar incidents with their memory entries
        """
        if not self.enabled:
            return []
        
        try:
            # Create query text from incident
            query_text = self._create_query_text(incident)
            
            # Search collection
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Parse results
            similar_incidents = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i, incident_id in enumerate(results['ids'][0]):
                    try:
                        # Parse stored document
                        doc_data = json.loads(results['documents'][0][i])
                        metadata = results['metadatas'][0][i]
                        distance = results['distances'][0][i] if 'distances' in results else None
                        
                        similar_incidents.append({
                            'incident_id': incident_id,
                            'incident': doc_data.get('incident', {}),
                            'memory': doc_data.get('memory', {}),
                            'similarity_score': 1.0 - (distance if distance else 0.5),
                            'metadata': metadata
                        })
                    except Exception as e:
                        logger.warning(f"Failed to parse result {i}: {str(e)}")
            
            logger.info(f"Found {len(similar_incidents)} similar incidents")
            return similar_incidents
        except Exception as e:
            logger.error(f"Failed to search vector memory: {str(e)}")
            return []
    
    def search_by_pattern(self, 
                         pattern: str, 
                         n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for incidents matching a specific pattern
        
        Args:
            pattern: Pattern description to search for
            n_results: Number of results to return
            
        Returns:
            List of matching incidents
        """
        if not self.enabled:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[pattern],
                n_results=n_results
            )
            
            matching_incidents = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i, incident_id in enumerate(results['ids'][0]):
                    try:
                        doc_data = json.loads(results['documents'][0][i])
                        matching_incidents.append({
                            'incident_id': incident_id,
                            'memory': doc_data.get('memory', {}),
                            'metadata': results['metadatas'][0][i]
                        })
                    except Exception as e:
                        logger.warning(f"Failed to parse result {i}: {str(e)}")
            
            return matching_incidents
        except Exception as e:
            logger.error(f"Failed to search by pattern: {str(e)}")
            return []
    
    def get_prevention_rules(self, 
                            finding_types: List[str], 
                            n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Get prevention rules for specific finding types
        
        Args:
            finding_types: List of finding types
            n_results: Number of results to return
            
        Returns:
            List of relevant prevention rules
        """
        if not self.enabled:
            return []
        
        query = f"Prevention rules for: {', '.join(finding_types)}"
        return self.search_by_pattern(query, n_results)
    
    def _create_searchable_text(self, 
                               incident: Dict[str, Any], 
                               memory_entry: Dict[str, Any]) -> str:
        """Create searchable text from incident and memory"""
        parts = []
        
        # Incident information
        parts.append(f"Title: {incident.get('title', '')}")
        parts.append(f"Pattern: {memory_entry.get('incident_pattern', '')}")
        parts.append(f"Root Cause: {memory_entry.get('root_cause', '')}")
        
        # Finding types
        finding_types = self._extract_finding_types(incident)
        if finding_types:
            parts.append(f"Finding Types: {', '.join(finding_types)}")
        
        # Signals to watch
        signals = memory_entry.get('signals_to_watch', [])
        if signals:
            parts.append(f"Signals: {', '.join(signals)}")
        
        # Prevention rule
        prevention_rule = memory_entry.get('prevention_rule', '')
        if prevention_rule:
            parts.append(f"Prevention: {prevention_rule}")
        
        # Affected resources
        affected_repos = incident.get('affected_repos', [])
        if affected_repos:
            parts.append(f"Repos: {', '.join(affected_repos)}")
        
        affected_endpoints = incident.get('affected_endpoints', [])
        if affected_endpoints:
            parts.append(f"Endpoints: {', '.join(affected_endpoints)}")
        
        affected_tables = incident.get('affected_database_tables', [])
        if affected_tables:
            parts.append(f"Tables: {', '.join(affected_tables)}")
        
        return ' | '.join(parts)
    
    def _create_query_text(self, incident: Dict[str, Any]) -> str:
        """Create query text from incident"""
        parts = []
        
        parts.append(f"Title: {incident.get('title', '')}")
        
        finding_types = self._extract_finding_types(incident)
        if finding_types:
            parts.append(f"Finding Types: {', '.join(finding_types)}")
        
        affected_repos = incident.get('affected_repos', [])
        if affected_repos:
            parts.append(f"Repos: {', '.join(affected_repos)}")
        
        affected_endpoints = incident.get('affected_endpoints', [])
        if affected_endpoints:
            parts.append(f"Endpoints: {', '.join(affected_endpoints)}")
        
        return ' | '.join(parts)
    
    def _extract_finding_types(self, incident: Dict[str, Any]) -> List[str]:
        """Extract unique finding types from incident"""
        findings = incident.get('findings', [])
        finding_types = list(set(f.get('finding_type', '') for f in findings if f.get('finding_type')))
        return finding_types
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector memory statistics"""
        if not self.enabled:
            return {
                'enabled': False,
                'total_entries': 0
            }
        
        try:
            count = self.collection.count()
            return {
                'enabled': True,
                'total_entries': count,
                'collection_name': self.collection_name,
                'storage_path': str(self.storage_path)
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {
                'enabled': True,
                'total_entries': 0,
                'error': str(e)
            }
    
    def clear(self):
        """Clear all vector memory (use with caution)"""
        if not self.enabled:
            return
        
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Security incident patterns and prevention rules"}
            )
            logger.info("Vector memory cleared")
        except Exception as e:
            logger.error(f"Failed to clear vector memory: {str(e)}")


# Made with Bob