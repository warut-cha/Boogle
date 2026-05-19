"""
Code Collector
Scans repositories and collects source code files for analysis
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Set
import logging

logger = logging.getLogger(__name__)


class CodeCollector:
    """Collects source code files from repositories"""
    
    def __init__(self, path: str, config: Dict[str, Any]):
        """
        Initialize code collector
        
        Args:
            path: Path to scan (file, directory, or repository)
            config: Analysis configuration
        """
        self.path = Path(path)
        self.config = config
        self.scan_patterns = config.get('static_analysis', {}).get('scan_patterns', ['*'])
        self.exclude_patterns = config.get('static_analysis', {}).get('exclude_patterns', [])
        self.max_file_size_mb = config.get('static_analysis', {}).get('max_file_size_mb', 10)
        self.files_collected: List[Dict[str, Any]] = []
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect all relevant source code files
        
        Returns:
            Dictionary containing collected files and metadata
        """
        logger.info(f"Starting code collection from: {self.path}")
        
        if not self.path.exists():
            raise FileNotFoundError(f"Path does not exist: {self.path}")
        
        if self.path.is_file():
            self._collect_file(self.path)
        elif self.path.is_dir():
            self._collect_directory(self.path)
        else:
            raise ValueError(f"Invalid path type: {self.path}")
        
        logger.info(f"Collected {len(self.files_collected)} files")
        
        return {
            'path': str(self.path),
            'files': self.files_collected,
            'total_files': len(self.files_collected),
            'total_size_bytes': sum(f['size'] for f in self.files_collected)
        }
    
    def _collect_directory(self, directory: Path):
        """Recursively collect files from directory"""
        for item in directory.rglob('*'):
            if item.is_file():
                # Check if file should be excluded
                if self._should_exclude(item):
                    continue
                
                # Check if file matches scan patterns
                if self._matches_scan_pattern(item):
                    self._collect_file(item)
    
    def _collect_file(self, file_path: Path):
        """Collect a single file"""
        try:
            # Check file size
            file_size = file_path.stat().st_size
            max_size_bytes = self.max_file_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                logger.warning(f"Skipping large file: {file_path} ({file_size} bytes)")
                return
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    logger.warning(f"Could not read file {file_path}: {str(e)}")
                    return
            
            file_info = {
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(self.path.parent)),
                'name': file_path.name,
                'extension': file_path.suffix,
                'size': file_size,
                'content': content,
                'line_count': len(content.split('\n'))
            }
            
            self.files_collected.append(file_info)
            logger.debug("Collected code data successfully")
            
        except Exception as e:
            logger.error(f"Error collecting file {file_path}: {str(e)}")
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded"""
        path_str = str(path)
        
        for pattern in self.exclude_patterns:
            # Simple pattern matching (can be enhanced with fnmatch)
            pattern_clean = pattern.replace('*/', '').replace('/*', '')
            if pattern_clean in path_str:
                return True
        
        return False
    
    def _matches_scan_pattern(self, path: Path) -> bool:
        """Check if file matches scan patterns"""
        if '*' in self.scan_patterns:
            return True
        
        extension = path.suffix
        
        for pattern in self.scan_patterns:
            if pattern.startswith('*.'):
                # Extension pattern
                if extension == pattern[1:]:
                    return True
            elif pattern in path.name:
                return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics"""
        extensions = {}
        total_lines = 0
        
        for file_info in self.files_collected:
            ext = file_info['extension'] or 'no_extension'
            extensions[ext] = extensions.get(ext, 0) + 1
            total_lines += file_info['line_count']
        
        return {
            'total_files': len(self.files_collected),
            'total_lines': total_lines,
            'by_extension': extensions,
            'total_size_mb': sum(f['size'] for f in self.files_collected) / (1024 * 1024)
        }

# Made with Bob
