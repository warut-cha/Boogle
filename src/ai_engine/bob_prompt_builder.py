"""
Bob Prompt Builder
Constructs prompts for IBM Bob (watsonx.ai) security analysis
"""

import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class BobPromptBuilder:
    """Builds structured prompts for IBM Bob security analysis"""
    
    def __init__(self):
        """Initialize prompt builder"""
        self.system_context = """You are Bob, an expert DevSecOps AI assistant specializing in security analysis.
Your role is to analyze security incidents, identify attack patterns, recommend fixes, generate security tests, and create incident reports.
You provide actionable, specific recommendations based on evidence and best practices."""
    
    def build_prompt(self, bob_input: Dict[str, Any]) -> str:
        """
        Build complete prompt from Bob input
        
        Args:
            bob_input: Bob input JSON with incident, attack_path, confidence, etc.
            
        Returns:
            Formatted prompt string
        """
        incident = bob_input.get('incident', {})
        attack_path = bob_input.get('attack_path', {})
        confidence = bob_input.get('confidence', {})
        related_memory = bob_input.get('related_memory', [])
        requested_outputs = bob_input.get('requested_outputs', [])
        
        prompt_parts = []
        
        # System context
        prompt_parts.append(self.system_context)
        prompt_parts.append("\n---\n")
        
        # Incident information
        prompt_parts.append("## SECURITY INCIDENT ANALYSIS REQUEST\n")
        prompt_parts.append(self._format_incident(incident))
        
        # Attack path
        if attack_path and attack_path.get('nodes'):
            prompt_parts.append("\n## ATTACK PATH\n")
            prompt_parts.append(self._format_attack_path(attack_path))
        
        # Confidence assessment
        if confidence:
            prompt_parts.append("\n## CONFIDENCE ASSESSMENT\n")
            prompt_parts.append(self._format_confidence(confidence))
        
        # Related memory (past similar incidents)
        if related_memory:
            prompt_parts.append("\n## RELATED PAST INCIDENTS\n")
            prompt_parts.append(self._format_related_memory(related_memory))
        
        # Request specific outputs
        prompt_parts.append("\n## REQUESTED ANALYSIS\n")
        prompt_parts.append(self._format_requested_outputs(requested_outputs, incident))
        
        # Output format instructions
        prompt_parts.append("\n## OUTPUT FORMAT\n")
        prompt_parts.append(self._get_output_format_instructions())
        
        return "\n".join(prompt_parts)
    
    def _format_incident(self, incident: Dict[str, Any]) -> str:
        """Format incident information"""
        lines = []
        
        lines.append(f"**Incident ID:** {incident.get('incident_id', 'UNKNOWN')}")
        lines.append(f"**Title:** {incident.get('title', 'Untitled')}")
        lines.append(f"**Severity:** {incident.get('severity', 'medium')}")
        lines.append(f"**Severity Level:** {incident.get('severity_level', 3)}/5")
        
        if incident.get('affected_repos'):
            lines.append(f"**Affected Repositories:** {', '.join(incident['affected_repos'])}")
        
        if incident.get('affected_files'):
            lines.append(f"**Affected Files:** {', '.join(incident['affected_files'][:5])}")
            if len(incident['affected_files']) > 5:
                lines.append(f"  _(and {len(incident['affected_files']) - 5} more)_")
        
        if incident.get('affected_endpoints'):
            lines.append(f"**Affected Endpoints:** {', '.join(incident['affected_endpoints'])}")
        
        if incident.get('affected_database_tables'):
            lines.append(f"**Affected Database Tables:** {', '.join(incident['affected_database_tables'])}")
        
        # Findings summary
        findings = incident.get('findings', [])
        if findings:
            lines.append(f"\n**Findings ({len(findings)}):**")
            for i, finding in enumerate(findings[:10], 1):
                finding_type = finding.get('finding_type', 'unknown')
                severity = finding.get('severity_hint', 'medium')
                file_path = finding.get('file', 'unknown')
                evidence = finding.get('evidence', '')
                
                lines.append(f"{i}. [{severity.upper()}] {finding_type}")
                lines.append(f"   - File: {file_path}")
                if evidence:
                    lines.append(f"   - Evidence: {evidence[:100]}")
            
            if len(findings) > 10:
                lines.append(f"   _(and {len(findings) - 10} more findings)_")
        
        return "\n".join(lines)
    
    def _format_attack_path(self, attack_path: Dict[str, Any]) -> str:
        """Format attack path graph"""
        lines = []
        
        nodes = attack_path.get('nodes', [])
        edges = attack_path.get('edges', [])
        
        if nodes:
            lines.append("**Attack Progression:**")
            
            # Create a simple text representation of the graph
            node_map = {node['id']: node for node in nodes}
            
            # Build adjacency list
            adjacency = {}
            for edge in edges:
                from_id = edge.get('from')
                to_id = edge.get('to')
                label = edge.get('label', 'leads to')
                
                if from_id not in adjacency:
                    adjacency[from_id] = []
                adjacency[from_id].append((to_id, label))
            
            # Traverse and format
            visited = set()
            
            def format_node(node_id: str, depth: int = 0):
                if node_id in visited or node_id not in node_map:
                    return []
                
                visited.add(node_id)
                node = node_map[node_id]
                indent = "  " * depth
                result = [f"{indent}→ {node.get('label', 'Unknown')} ({node.get('type', 'unknown')})"]
                
                if node_id in adjacency:
                    for next_id, edge_label in adjacency[node_id]:
                        result.append(f"{indent}  ↓ {edge_label}")
                        result.extend(format_node(next_id, depth + 1))
                
                return result
            
            # Start from first node
            if nodes:
                lines.extend(format_node(nodes[0]['id']))
        
        return "\n".join(lines)
    
    def _format_confidence(self, confidence: Dict[str, Any]) -> str:
        """Format confidence assessment"""
        lines = []
        
        score = confidence.get('score', 0.0)
        lines.append(f"**Confidence Score:** {score:.2f} ({self._confidence_level(score)})")
        
        reasons = confidence.get('reasons', [])
        if reasons:
            lines.append("\n**Supporting Evidence:**")
            for reason in reasons:
                lines.append(f"- ✓ {reason}")
        
        limitations = confidence.get('limitations', [])
        if limitations:
            lines.append("\n**Limitations:**")
            for limitation in limitations:
                lines.append(f"- ⚠ {limitation}")
        
        return "\n".join(lines)
    
    def _confidence_level(self, score: float) -> str:
        """Convert confidence score to level"""
        if score >= 0.9:
            return "Very High"
        elif score >= 0.75:
            return "High"
        elif score >= 0.6:
            return "Medium"
        elif score >= 0.4:
            return "Low"
        else:
            return "Very Low"
    
    def _format_related_memory(self, related_memory: List[Dict[str, Any]]) -> str:
        """Format related past incidents"""
        lines = []
        
        lines.append("The following similar incidents were found in memory:")
        
        for i, memory in enumerate(related_memory[:3], 1):
            mem_data = memory.get('memory', {})
            similarity = memory.get('similarity_score', 0.0)
            
            lines.append(f"\n**Similar Incident {i}** (Similarity: {similarity:.2f})")
            lines.append(f"- Pattern: {mem_data.get('incident_pattern', 'Unknown')}")
            lines.append(f"- Root Cause: {mem_data.get('root_cause', 'Unknown')}")
            
            prevention = mem_data.get('prevention_rule', '')
            if prevention:
                lines.append(f"- Prevention Rule: {prevention[:200]}")
        
        return "\n".join(lines)
    
    def _format_requested_outputs(self, requested_outputs: List[str], incident: Dict[str, Any]) -> str:
        """Format requested analysis outputs"""
        lines = []
        
        lines.append("Please provide the following analysis:")
        
        output_descriptions = {
            'attack_explanation': '1. **Attack Type & Target**: Explain what type of attack this is and what the target is',
            'target_analysis': '2. **Target Analysis**: Detailed analysis of affected systems and data',
            'fix_plan': '3. **Recommended Fixes**: Specific, actionable fixes categorized by type (immediate_action, code_fix, api_fix, infrastructure_fix)',
            'security_tests': '4. **Security Tests**: Generate 3-5 Python security tests with actual test code',
            'incident_report': '5. **Incident Report**: Professional markdown incident report',
            'ai_memory': '6. **AI Memory**: Prevention rule to learn from this incident',
            'pr_draft': '7. **PR Draft**: Pull request with branch name, title, description, and files to change'
        }
        
        if requested_outputs:
            for output in requested_outputs:
                if output in output_descriptions:
                    lines.append(output_descriptions[output])
        else:
            # Default: all outputs
            for desc in output_descriptions.values():
                lines.append(desc)
        
        return "\n".join(lines)
    
    def _get_output_format_instructions(self) -> str:
        """Get output format instructions"""
        return """Please provide your analysis in the following JSON format:

```json
{
  "attack_type": "Brief description of attack type",
  "target": "What systems/data are targeted",
  "severity": "critical|high|medium|low",
  "confidence_assessment": "Your assessment of the confidence score and evidence",
  "recommended_fixes": [
    {
      "type": "immediate_action|code_fix|api_fix|infrastructure_fix",
      "description": "Specific fix description",
      "file": "path/to/file (if applicable)",
      "endpoint": "/api/endpoint (if applicable)"
    }
  ],
  "generated_security_tests": [
    {
      "file": "tests/test_name.py",
      "name": "test_function_name",
      "purpose": "What this test verifies",
      "code": "def test_function_name():\\n    # Actual Python test code\\n    assert True"
    }
  ],
  "incident_report": "# Markdown formatted incident report\\n\\n## Summary\\n...",
  "ai_memory": {
    "memory_type": "security_prevention_rule",
    "incident_pattern": "pattern_name",
    "root_cause": "Root cause description",
    "signals_to_watch": ["signal1", "signal2"],
    "prevention_rule": "Prevention rule description",
    "recommended_tests": ["test1", "test2"],
    "severity_escalation_conditions": ["condition1", "condition2"]
  },
  "pr_draft": {
    "branch_name": "security/fix-description",
    "pr_title": "Security: Fix title",
    "pr_description": "PR description with changes and testing",
    "files_to_change": ["file1.py", "file2.py"]
  }
}
```

Provide ONLY the JSON output, no additional text before or after."""


# Made with Bob