"""
PR Draft Generator
Generates pull request drafts from Bob's security analysis
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class PRDraftGenerator:
    """Generates pull request drafts for security fixes"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize PR draft generator
        
        Args:
            config: PR generation configuration
        """
        self.config = config
        self.output_dir = Path(config.get('output_directory', './generated_reports'))
        self.template_style = config.get('template_style', 'github')
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_pr_draft(self, 
                         bob_output: Dict[str, Any], 
                         incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate PR draft from Bob's analysis
        
        Args:
            bob_output: Bob's output with pr_draft
            incident: Original incident data
            
        Returns:
            PR draft information with file path
        """
        pr_draft = bob_output.get('pr_draft', {})
        
        if not pr_draft:
            logger.warning("No PR draft in Bob output, generating default")
            pr_draft = self._generate_default_pr_draft(incident, bob_output)
        
        # Generate PR description file
        pr_file = self._generate_pr_file(pr_draft, incident, bob_output)
        
        # Generate git commands file
        git_commands_file = self._generate_git_commands(pr_draft, incident)
        
        return {
            'branch_name': pr_draft.get('branch_name', 'security/fix'),
            'pr_title': pr_draft.get('pr_title', 'Security Fix'),
            'pr_description_file': pr_file,
            'git_commands_file': git_commands_file,
            'files_to_change': pr_draft.get('files_to_change', [])
        }
    
    def _generate_pr_file(self, 
                         pr_draft: Dict[str, Any], 
                         incident: Dict[str, Any],
                         bob_output: Dict[str, Any]) -> str:
        """Generate PR description markdown file"""
        incident_id = incident.get('incident_id', 'INC-UNKNOWN')
        branch_name = pr_draft.get('branch_name', 'security/fix')
        
        # Sanitize branch name for filename
        safe_branch = branch_name.replace('/', '-')
        pr_file_path = self.output_dir / f'PR_DRAFT_{safe_branch}_{incident_id}.md'
        
        # Build PR description
        content = self._build_pr_description(pr_draft, incident, bob_output)
        
        # Write file
        with open(pr_file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Generated PR draft: {pr_file_path}")
        return str(pr_file_path)
    
    def _build_pr_description(self, 
                             pr_draft: Dict[str, Any], 
                             incident: Dict[str, Any],
                             bob_output: Dict[str, Any]) -> str:
        """Build complete PR description"""
        incident_id = incident.get('incident_id', 'INC-UNKNOWN')
        title = pr_draft.get('pr_title', 'Security Fix')
        description = pr_draft.get('pr_description', '')
        
        # If description is provided, use it
        if description and len(description) > 100:
            return description
        
        # Otherwise, build comprehensive description
        content = f'''# {title}

## 🔒 Security Fix for Incident {incident_id}

### Issue Summary
{incident.get('title', 'Security incident detected')}

**Severity:** {incident.get('severity', 'medium').upper()}  
**Confidence Score:** {incident.get('confidence_score', 0.75):.2f}

### Problem Description
'''
        
        # Add attack type and target from Bob
        attack_type = bob_output.get('attack_type', 'Security vulnerability')
        target = bob_output.get('target', 'System resources')
        
        content += f"{attack_type} affecting {target}.\n\n"
        
        # Add confidence assessment
        confidence_assessment = bob_output.get('confidence_assessment', '')
        if confidence_assessment:
            content += f"**Analysis:** {confidence_assessment}\n\n"
        
        # Add findings summary
        findings = incident.get('findings', [])
        if findings:
            content += "### Findings\n\n"
            for i, finding in enumerate(findings[:5], 1):
                finding_type = finding.get('finding_type', 'unknown')
                file_path = finding.get('file', 'unknown')
                content += f"{i}. **{finding_type}** in `{file_path}`\n"
            
            if len(findings) > 5:
                content += f"\n_...and {len(findings) - 5} more findings_\n"
            content += "\n"
        
        # Add changes section
        content += "### Changes Made\n\n"
        
        recommended_fixes = bob_output.get('recommended_fixes', [])
        if recommended_fixes:
            for fix in recommended_fixes:
                fix_type = fix.get('type', 'fix')
                fix_desc = fix.get('description', 'Security fix')
                content += f"- **{fix_type.replace('_', ' ').title()}:** {fix_desc}\n"
        else:
            content += "- Security vulnerabilities addressed\n"
            content += "- Code hardening implemented\n"
        
        content += "\n"
        
        # Add files changed
        files_to_change = pr_draft.get('files_to_change', [])
        if files_to_change:
            content += "### Files Modified\n\n"
            for file_path in files_to_change[:10]:
                content += f"- `{file_path}`\n"
            
            if len(files_to_change) > 10:
                content += f"\n_...and {len(files_to_change) - 10} more files_\n"
            content += "\n"
        
        # Add testing section
        content += "### Testing\n\n"
        
        generated_tests = bob_output.get('generated_security_tests', [])
        if generated_tests:
            content += "**Security Tests Added:**\n\n"
            for test in generated_tests[:5]:
                test_name = test.get('name', 'test')
                test_purpose = test.get('purpose', 'Security test')
                content += f"- `{test_name}`: {test_purpose}\n"
            content += "\n"
        
        content += "**Test Results:**\n\n"
        content += "- [ ] All existing tests pass\n"
        content += "- [ ] New security tests pass\n"
        content += "- [ ] No hardcoded secrets detected\n"
        content += "- [ ] Security scan passes\n\n"
        
        # Add security checklist
        content += "### Security Checklist\n\n"
        content += "- [ ] Credentials rotated (if applicable)\n"
        content += "- [ ] Secrets moved to environment variables\n"
        content += "- [ ] Access controls verified\n"
        content += "- [ ] Input validation implemented\n"
        content += "- [ ] Security tests added\n"
        content += "- [ ] Documentation updated\n"
        content += "- [ ] Code review completed\n\n"
        
        # Add deployment notes
        content += "### Deployment Notes\n\n"
        
        immediate_actions = [f for f in recommended_fixes if f.get('type') == 'immediate_action']
        if immediate_actions:
            content += "**⚠️ Immediate Actions Required Before Deployment:**\n\n"
            for action in immediate_actions:
                content += f"- {action.get('description', 'Action required')}\n"
            content += "\n"
        
        content += "**Post-Deployment:**\n\n"
        content += "- Monitor for any unusual activity\n"
        content += "- Verify security controls are working\n"
        content += "- Review logs for anomalies\n\n"
        
        # Add related incident info
        content += f"### Related Information\n\n"
        content += f"- **Incident ID:** {incident_id}\n"
        content += f"- **Incident Report:** See generated incident report\n"
        
        if incident.get('affected_repos'):
            content += f"- **Affected Repositories:** {', '.join(incident['affected_repos'])}\n"
        
        content += "\n---\n"
        content += f"*Generated by IBM Bob Sentinel on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return content
    
    def _generate_git_commands(self, 
                              pr_draft: Dict[str, Any], 
                              incident: Dict[str, Any]) -> str:
        """Generate git commands file"""
        incident_id = incident.get('incident_id', 'INC-UNKNOWN')
        branch_name = pr_draft.get('branch_name', 'security/fix')
        pr_title = pr_draft.get('pr_title', 'Security Fix')
        
        safe_branch = branch_name.replace('/', '-')
        commands_file = self.output_dir / f'GIT_COMMANDS_{safe_branch}_{incident_id}.sh'
        
        content = f'''#!/bin/bash
# Git commands for security fix PR
# Generated by IBM Bob Sentinel
# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

set -e  # Exit on error

echo "Creating security fix branch..."

# Create and checkout new branch
git checkout -b {branch_name}

# Stage changes
echo "Staging changes..."
'''
        
        files_to_change = pr_draft.get('files_to_change', [])
        if files_to_change:
            for file_path in files_to_change:
                content += f'git add "{file_path}"\n'
        else:
            content += 'git add .\n'
        
        content += f'''
# Commit changes
echo "Committing changes..."
git commit -m "{pr_title}

Fixes incident {incident_id}

- Security vulnerabilities addressed
- Tests added
- Documentation updated

Generated by IBM Bob Sentinel"

# Push branch
echo "Pushing branch..."
git push -u origin {branch_name}

echo ""
echo "✓ Branch pushed successfully!"
echo ""
echo "Next steps:"
echo "1. Go to your repository on GitHub/GitLab"
echo "2. Create a pull request from '{branch_name}' to 'develop'"
echo "3. Use the PR description from: PR_DRAFT_{safe_branch}_{incident_id}.md"
echo "4. Request review from security team"
echo ""
'''
        
        with open(commands_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make executable on Unix systems
        try:
            os.chmod(commands_file, 0o755)
        except:
            pass
        
        logger.info(f"Generated git commands: {commands_file}")
        return str(commands_file)
    
    def _generate_default_pr_draft(self, 
                                   incident: Dict[str, Any],
                                   bob_output: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default PR draft when not provided"""
        incident_id = incident.get('incident_id', 'INC-UNKNOWN')
        title = incident.get('title', 'Security Issue')
        
        return {
            'branch_name': f"security/fix-{incident_id.lower()}",
            'pr_title': f"Security: Fix {title}",
            'pr_description': f"Addresses security incident {incident_id}",
            'files_to_change': incident.get('affected_files', [])
        }
    
    def generate_pr_drafts_batch(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate PR drafts for multiple incidents
        
        Args:
            incidents: List of incidents with Bob analysis
            
        Returns:
            List of PR draft information
        """
        pr_drafts = []
        
        for incident in incidents:
            bob_analysis = incident.get('bob_analysis', {})
            if bob_analysis:
                try:
                    pr_info = self.generate_pr_draft(bob_analysis, incident)
                    pr_drafts.append(pr_info)
                except Exception as e:
                    logger.error(f"Failed to generate PR for incident {incident.get('incident_id')}: {str(e)}")
        
        logger.info(f"Generated {len(pr_drafts)} PR drafts")
        return pr_drafts


# Made with Bob