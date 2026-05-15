"""
Log Collector
Collects and parses log files for runtime analysis
"""

from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class LogCollector:
    """Collects log files for analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize log collector"""
        self.config = config
        self.log_paths = []
    
    def collect(self, log_path: str = './mock_data/logs/app.log') -> Dict[str, Any]:
        """
        Collect log files
        
        Args:
            log_path: Path to log file or directory
            
        Returns:
            Dictionary containing log data
        """
        path = Path(log_path)
        
        if path.is_file():
            self.log_paths.append(str(path))
        elif path.is_dir():
            # Collect all .log files
            self.log_paths.extend([str(p) for p in path.glob('*.log')])
        
        return {
            'log_files': self.log_paths,
            'total_files': len(self.log_paths)
        }

# Made with Bob
