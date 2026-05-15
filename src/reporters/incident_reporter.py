"""
Incident Reporter
Generates professional incident reports in multiple formats (Markdown, JSON, HTML)
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class IncidentReporter:
    """Generates incident reports in multiple formats"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize incident reporter
        
        Args:
            config: Reporting configuration
        """
        self.config = config
        self.output_dir = Path(config.get('output_directory', './output'))
        self.formats = config.get('formats', ['markdown', 'json'])
        self.include_code_snippets = config.get('include_code_snippets', True)
        self.max_snippet_lines = config.get('max_snippet_lines', 20)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_reports(self, incidents: List[Dict[str, Any]], 
                        output_dir: str = None,
                        formats: List[str] = None) -> List[str]:
        """
        Generate reports for all incidents
        
        Args:
            incidents: List of incidents
            output_dir: Optional output directory override
            formats: Optional formats override
            
        Returns:
            List of generated report file paths
        """
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if formats:
            self.formats = formats
        
        report_paths = []
        
        # Generate summary report
        summary_paths = self._generate_summary_report(incidents)
        report_paths.extend(summary_paths)
        
        # Generate individual incident reports
        for incident in incidents:
            incident_paths = self._generate_incident_report(incident)
            report_paths.extend(incident_paths)
        
        logger.info(f"Generated {len(report_paths)} report files")
        return report_paths
    
    def _generate_summary_report(self, incidents: List[Dict[str, Any]]) -> List[str]:
        """Generate summary report for all incidents"""
        paths = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if 'markdown' in self.formats:
            path = self.output_dir / f'security_analysis_summary_{timestamp}.md'
            self._write_markdown_summary(incidents, path)
            paths.append(str(path))
        
        if 'json' in self.formats:
            path = self.output_dir / f'security_analysis_summary_{timestamp}.json'
            self._write_json_summary(incidents, path)
            paths.append(str(path))
        
        if 'html' in self.formats:
            path = self.output_dir / f'security_analysis_summary_{timestamp}.html'
            self._write_html_summary(incidents, path)
            paths.append(str(path))
        
        return paths
    
    def _generate_incident_report(self, incident: Dict[str, Any]) -> List[str]:
        """Generate report for single incident"""
        paths = []
        incident_id = incident.get('id', 'UNKNOWN')
        
        if 'markdown' in self.formats:
            path = self.output_dir / f'{incident_id}.md'
            self._write_markdown_incident(incident, path)
            paths.append(str(path))
        
        if 'json' in self.formats:
            path = self.output_dir / f'{incident_id}.json'
            self._write_json_incident(incident, path)
            paths.append(str(path))
        
        return paths
    
    def _write_markdown_summary(self, incidents: List[Dict[str, Any]], path: Path):
        """Write summary report in Markdown format"""
        content = []
        
        # Header
        content.append("# Security Analysis Report")
        content.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"\n**Total Incidents:** {len(incidents)}\n")
        
        # Executive Summary
        content.append("## Executive Summary\n")
        
        severity_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for incident in incidents:
            level = incident.get('severity', {}).get('level', 3)
            severity_counts[level] += 1
        
        content.append("### Severity Distribution\n")
        content.append(f"- 🔴 **Critical (Level 5):** {severity_counts[5]}")
        content.append(f"- 🟠 **High (Level 4):** {severity_counts[4]}")
        content.append(f"- 🟡 **Medium (Level 3):** {severity_counts[3]}")
        content.append(f"- 🔵 **Low (Level 2):** {severity_counts[2]}")
        content.append(f"- ⚪ **Informational (Level 1):** {severity_counts[1]}\n")
        
        # Critical Incidents
        critical_incidents = [i for i in incidents if i.get('severity', {}).get('level', 0) == 5]
        if critical_incidents:
            content.append("## 🚨 Critical Incidents\n")
            for incident in critical_incidents:
                content.append(f"### {incident.get('title', 'Untitled')}")
                content.append(f"- **ID:** {incident.get('id')}")
                content.append(f"- **Type:** {incident.get('type')}")
                content.append(f"- **Confidence:** {incident.get('severity', {}).get('confidence', 0):.2f}")
                content.append(f"- **Description:** {incident.get('description', 'No description')}\n")
        
        # High Priority Incidents
        high_incidents = [i for i in incidents if i.get('severity', {}).get('level', 0) == 4]
        if high_incidents:
            content.append("## ⚠️ High Priority Incidents\n")
            for incident in high_incidents:
                content.append(f"### {incident.get('title', 'Untitled')}")
                content.append(f"- **ID:** {incident.get('id')}")
                content.append(f"- **Findings:** {incident.get('finding_count', 0)}")
                content.append(f"- **Description:** {incident.get('description', 'No description')}\n")
        
        # Recommendations
        content.append("## Recommendations\n")
        content.append("1. **Immediate Actions:**")
        content.append("   - Review and address all Critical incidents immediately")
        content.append("   - Rotate any exposed credentials")
        content.append("   - Block suspicious IP addresses\n")
        
        content.append("2. **Short-term Actions:**")
        content.append("   - Fix High priority vulnerabilities within 7 days")
        content.append("   - Implement recommended security tests")
        content.append("   - Update security policies\n")
        
        content.append("3. **Long-term Actions:**")
        content.append("   - Conduct security training for development team")
        content.append("   - Implement automated security scanning in CI/CD")
        content.append("   - Regular security audits\n")
        
        # Write to file
        with open(path, 'w') as f:
            f.write('\n'.join(content))
        
        logger.info(f"Generated Markdown summary: {path}")
    
    def _write_markdown_incident(self, incident: Dict[str, Any], path: Path):
        """Write incident report in Markdown format"""
        content = []
        
        # Header
        incident_id = incident.get('id', 'UNKNOWN')
        title = incident.get('title', 'Untitled Incident')
        
        content.append(f"# Security Incident Report: {incident_id}")
        content.append(f"\n## {title}\n")
        
        # Metadata
        content.append("### Incident Details\n")
        content.append(f"- **Incident ID:** {incident_id}")
        content.append(f"- **Timestamp:** {incident.get('timestamp', 'Unknown')}")
        content.append(f"- **Type:** {incident.get('type', 'Unknown')}")
        content.append(f"- **Correlation:** {incident.get('correlation_type', 'none')}")
        
        severity = incident.get('severity', {})
        level = severity.get('level', 3)
        level_name = severity.get('level_name', 'Medium')
        confidence = severity.get('confidence', 0.75)
        
        severity_emoji = {5: '🔴', 4: '🟠', 3: '🟡', 2: '🔵', 1: '⚪'}
        content.append(f"- **Severity:** {severity_emoji.get(level, '⚪')} Level {level} ({level_name})")
        content.append(f"- **Confidence:** {confidence:.2f}\n")
        
        # Description
        content.append("### Description\n")
        content.append(incident.get('description', 'No description available') + '\n')
        
        # Findings
        findings = incident.get('findings', [])
        content.append(f"### Findings ({len(findings)})\n")
        
        for i, finding in enumerate(findings, 1):
            content.append(f"#### Finding {i}: {finding.get('name', 'Unnamed')}\n")
            content.append(f"- **Type:** {finding.get('type')}")
            content.append(f"- **Severity:** {finding.get('severity')}")
            
            if 'file_path' in finding:
                content.append(f"- **Location:** {finding['file_path']}")
                if 'line_number' in finding:
                    content.append(f"  - Line {finding['line_number']}")
            
            content.append(f"- **Description:** {finding.get('description', 'No description')}")
            
            if 'remediation' in finding:
                content.append(f"- **Remediation:** {finding['remediation']}")
            
            content.append("")
        
        # Evidence
        content.append("### Evidence\n")
        evidence = incident.get('evidence', {})
        for key, value in evidence.items():
            content.append(f"- **{key}:** {value}")
        content.append("")
        
        # Remediation
        content.append("### Recommended Actions\n")
        content.append("#### Immediate Containment\n")
        
        if level >= 4:
            content.append("1. Isolate affected systems")
            content.append("2. Rotate compromised credentials")
            content.append("3. Block suspicious IP addresses")
            content.append("4. Enable enhanced monitoring\n")
        else:
            content.append("1. Review affected code/systems")
            content.append("2. Plan remediation timeline")
            content.append("3. Update security policies\n")
        
        content.append("#### Code Fixes\n")
        content.append("See individual finding remediations above.\n")
        
        content.append("#### Prevention\n")
        content.append("1. Implement security tests")
        content.append("2. Add to CI/CD pipeline")
        content.append("3. Update security training")
        content.append("4. Review similar code patterns\n")
        
        # Write to file
        with open(path, 'w') as f:
            f.write('\n'.join(content))
        
        logger.info(f"Generated Markdown incident report: {path}")
    
    def _write_json_summary(self, incidents: List[Dict[str, Any]], path: Path):
        """Write summary in JSON format"""
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_incidents': len(incidents),
            'severity_distribution': self._get_severity_distribution(incidents),
            'incidents': [
                {
                    'id': i.get('id'),
                    'title': i.get('title'),
                    'severity': i.get('severity'),
                    'type': i.get('type'),
                    'finding_count': i.get('finding_count', 0)
                }
                for i in incidents
            ]
        }
        
        with open(path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Generated JSON summary: {path}")
    
    def _write_json_incident(self, incident: Dict[str, Any], path: Path):
        """Write incident in JSON format"""
        with open(path, 'w') as f:
            json.dump(incident, f, indent=2)
        
        logger.info(f"Generated JSON incident report: {path}")
    
    def _write_html_summary(self, incidents: List[Dict[str, Any]], path: Path):
        """Write summary in HTML format"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Security Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .critical {{ color: #d32f2f; }}
        .high {{ color: #f57c00; }}
        .medium {{ color: #fbc02d; }}
        .low {{ color: #1976d2; }}
        .info {{ color: #757575; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>Security Analysis Report</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Total Incidents:</strong> {len(incidents)}</p>
    
    <h2>Severity Distribution</h2>
    <table>
        <tr>
            <th>Level</th>
            <th>Count</th>
        </tr>
"""
        
        severity_counts = self._get_severity_distribution(incidents)
        for level in [5, 4, 3, 2, 1]:
            level_name = {5: 'Critical', 4: 'High', 3: 'Medium', 2: 'Low', 1: 'Informational'}[level]
            css_class = {5: 'critical', 4: 'high', 3: 'medium', 2: 'low', 1: 'info'}[level]
            count = severity_counts.get(level, 0)
            html += f'        <tr><td class="{css_class}">{level_name}</td><td>{count}</td></tr>\n'
        
        html += """
    </table>
    
    <h2>Incidents</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Severity</th>
            <th>Findings</th>
        </tr>
"""
        
        for incident in incidents:
            incident_id = incident.get('id', 'UNKNOWN')
            title = incident.get('title', 'Untitled')
            level = incident.get('severity', {}).get('level', 3)
            level_name = incident.get('severity', {}).get('level_name', 'Medium')
            finding_count = incident.get('finding_count', 0)
            css_class = {5: 'critical', 4: 'high', 3: 'medium', 2: 'low', 1: 'info'}.get(level, 'info')
            
            html += f'        <tr><td>{incident_id}</td><td>{title}</td><td class="{css_class}">{level_name}</td><td>{finding_count}</td></tr>\n'
        
        html += """
    </table>
</body>
</html>
"""
        
        with open(path, 'w') as f:
            f.write(html)
        
        logger.info(f"Generated HTML summary: {path}")
    
    def _get_severity_distribution(self, incidents: List[Dict[str, Any]]) -> Dict[int, int]:
        """Get severity distribution"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for incident in incidents:
            level = incident.get('severity', {}).get('level', 3)
            distribution[level] += 1
        
        return distribution

# Made with Bob
