"""
Database Connection Manager
Handles connections to MongoDB and SQLite databases
"""

import os
from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.database import Database
import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize database manager
        
        Args:
            config: Database configuration dictionary
        """
        self.config = config
        self.db_type = config.get('type', 'mongodb')
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.sqlite_conn: Optional[sqlite3.Connection] = None
        
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            if self.db_type == 'mongodb':
                self._connect_mongodb()
            elif self.db_type == 'sqlite':
                self._connect_sqlite()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            logger.info(f"Connected to {self.db_type} database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def _connect_mongodb(self):
        """Connect to MongoDB"""
        mongo_config = self.config.get('mongodb', {})
        
        host = mongo_config.get('host', 'localhost')
        port = mongo_config.get('port', 27017)
        database = mongo_config.get('database', 'security_analyst')
        username = mongo_config.get('username')
        password = mongo_config.get('password')
        
        # Build connection string
        if username and password:
            connection_string = f"mongodb://{username}:{password}@{host}:{port}/"
        else:
            connection_string = f"mongodb://{host}:{port}/"
        
        self.client = MongoClient(connection_string)
        self.db = self.client[database]
        
        # Test connection
        self.client.server_info()
    
    def _connect_sqlite(self):
        """Connect to SQLite"""
        sqlite_config = self.config.get('sqlite', {})
        db_path = sqlite_config.get('path', './data/security_analyst.db')
        
        # Create directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.sqlite_conn = sqlite3.connect(db_path)
        self.sqlite_conn.row_factory = sqlite3.Row
    
    def initialize(self):
        """Initialize database schema"""
        if self.db_type == 'mongodb':
            self._initialize_mongodb()
        elif self.db_type == 'sqlite':
            self._initialize_sqlite()
    
    def _initialize_mongodb(self):
        """Initialize MongoDB collections"""
        collections = [
            'incidents',
            'findings',
            'ai_memory',
            'analysis_runs',
            'remediation_actions'
        ]
        
        existing_collections = self.db.list_collection_names()
        
        for collection in collections:
            if collection not in existing_collections:
                self.db.create_collection(collection)
                logger.info(f"Created collection: {collection}")
        
        # Create indexes
        self.db.incidents.create_index('incident_id', unique=True)
        self.db.incidents.create_index('severity.level')
        self.db.incidents.create_index('timestamp')
        
        self.db.findings.create_index('finding_id', unique=True)
        self.db.findings.create_index('type')
        self.db.findings.create_index('severity')
        
        self.db.ai_memory.create_index('incident_pattern')
        self.db.ai_memory.create_index('created_at')
        
        logger.info("MongoDB schema initialized")
    
    def _initialize_sqlite(self):
        """Initialize SQLite schema"""
        cursor = self.sqlite_conn.cursor()
        
        # Create incidents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                severity_level INTEGER NOT NULL,
                severity_confidence REAL NOT NULL,
                attack_type TEXT,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                data TEXT NOT NULL
            )
        ''')
        
        # Create findings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                finding_id TEXT UNIQUE NOT NULL,
                incident_id TEXT,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                file_path TEXT,
                line_number INTEGER,
                description TEXT,
                evidence TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
            )
        ''')
        
        # Create ai_memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_pattern TEXT NOT NULL,
                root_cause TEXT,
                prevention_rule TEXT,
                signals TEXT,
                recommended_tests TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Create analysis_runs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE NOT NULL,
                path TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT DEFAULT 'running',
                incidents_found INTEGER DEFAULT 0,
                findings_count INTEGER DEFAULT 0
            )
        ''')
        
        self.sqlite_conn.commit()
        logger.info("SQLite schema initialized")
    
    def save_incident(self, incident: Dict[str, Any]) -> str:
        """
        Save incident to database
        
        Args:
            incident: Incident data dictionary
            
        Returns:
            Incident ID
        """
        if self.db_type == 'mongodb':
            result = self.db.incidents.insert_one(incident)
            return str(result.inserted_id)
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute('''
                INSERT INTO incidents (
                    incident_id, title, severity_level, severity_confidence,
                    attack_type, timestamp, data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident['id'],
                incident['title'],
                incident['severity']['level'],
                incident['severity']['confidence'],
                incident.get('attack_type'),
                incident['timestamp'],
                str(incident)
            ))
            self.sqlite_conn.commit()
            return incident['id']
    
    def save_finding(self, finding: Dict[str, Any]) -> str:
        """
        Save finding to database
        
        Args:
            finding: Finding data dictionary
            
        Returns:
            Finding ID
        """
        if self.db_type == 'mongodb':
            result = self.db.findings.insert_one(finding)
            return str(result.inserted_id)
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute('''
                INSERT INTO findings (
                    finding_id, incident_id, type, severity, file_path,
                    line_number, description, evidence, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                finding['id'],
                finding.get('incident_id'),
                finding['type'],
                finding['severity'],
                finding.get('file_path'),
                finding.get('line_number'),
                finding.get('description'),
                finding.get('evidence'),
                finding['timestamp']
            ))
            self.sqlite_conn.commit()
            return finding['id']
    
    def save_ai_memory(self, memory: Dict[str, Any]) -> str:
        """
        Save AI memory entry
        
        Args:
            memory: Memory data dictionary
            
        Returns:
            Memory ID
        """
        if self.db_type == 'mongodb':
            result = self.db.ai_memory.insert_one(memory)
            return str(result.inserted_id)
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute('''
                INSERT INTO ai_memory (
                    incident_pattern, root_cause, prevention_rule,
                    signals, recommended_tests, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                memory['incident_pattern'],
                memory['root_cause'],
                memory['prevention_rule'],
                str(memory.get('signals_to_watch', [])),
                str(memory.get('recommended_tests', [])),
                memory['created_at']
            ))
            self.sqlite_conn.commit()
            return str(cursor.lastrowid)
    
    def get_incidents(self, filters: Optional[Dict[str, Any]] = None) -> list:
        """
        Retrieve incidents from database
        
        Args:
            filters: Optional filter criteria
            
        Returns:
            List of incidents
        """
        if self.db_type == 'mongodb':
            query = filters or {}
            return list(self.db.incidents.find(query))
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute('SELECT * FROM incidents')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_ai_memory(self) -> list:
        """
        Retrieve all AI memory entries
        
        Returns:
            List of memory entries
        """
        if self.db_type == 'mongodb':
            return list(self.db.ai_memory.find())
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute('SELECT * FROM ai_memory')
            return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
        
        if self.sqlite_conn:
            self.sqlite_conn.close()
            logger.info("SQLite connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

# Made with Bob
