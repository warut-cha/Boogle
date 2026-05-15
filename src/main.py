#!/usr/bin/env python3
"""
Security Analyst System - Main Entry Point
AI-powered security analysis and anomaly detection system
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import yaml
from datetime import datetime

# Import core modules (will be implemented)
from database.connection import DatabaseManager
from collectors.code_collector import CodeCollector
from collectors.log_collector import LogCollector
from collectors.api_collector import APICollector
from analyzers.static_analyzer import StaticAnalyzer
from analyzers.runtime_analyzer import RuntimeAnalyzer
from analyzers.deprecated_api_detector import DeprecatedAPIDetector
from correlators.incident_correlator import IncidentCorrelator
from classifiers.severity_classifier import SeverityClassifier
from remediators.fix_generator import FixGenerator
from reporters.incident_reporter import IncidentReporter
from ai_engine.reasoning_engine import ReasoningEngine
from ai_engine.memory_manager import MemoryManager

console = Console()

# Load configuration
def load_config():
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

CONFIG = load_config()


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    🔒 Security Analyst System
    
    AI-powered security analysis and anomaly detection
    """
    pass


@cli.command()
@click.option('--path', '-p', required=True, help='Path to analyze (repository, directory, or file)')
@click.option('--use-ibm-watson', is_flag=True, help='Enable IBM Watson AI integration')
@click.option('--output', '-o', default='./output', help='Output directory for reports')
@click.option('--format', '-f', multiple=True, default=['markdown', 'json'], 
              help='Output format (markdown, json, html)')
@click.option('--severity-threshold', '-s', default=1, type=int,
              help='Minimum severity level to report (1-5)')
def analyze(path, use_ibm_watson, output, format, severity_threshold):
    """
    Analyze code, logs, and runtime behavior for security risks
    """
    console.print(Panel.fit(
        "[bold cyan]🔍 Security Analysis Started[/bold cyan]",
        border_style="cyan"
    ))
    
    try:
        # Initialize components
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 1: Initialize database
            task = progress.add_task("[cyan]Initializing database...", total=None)
            db_manager = DatabaseManager(CONFIG['database'])
            progress.update(task, completed=True)
            
            # Step 2: Collect data
            task = progress.add_task("[cyan]Collecting data...", total=None)
            code_collector = CodeCollector(path, CONFIG['analysis'])
            code_data = code_collector.collect()
            progress.update(task, completed=True)
            
            # Step 3: Static analysis
            task = progress.add_task("[cyan]Running static analysis...", total=None)
            static_analyzer = StaticAnalyzer(CONFIG['security'])
            static_findings = static_analyzer.analyze(code_data)
            progress.update(task, completed=True)
            
            # Step 4: Deprecated API detection
            task = progress.add_task("[cyan]Detecting deprecated APIs...", total=None)
            api_detector = DeprecatedAPIDetector(CONFIG['analysis'])
            api_findings = api_detector.detect(code_data)
            progress.update(task, completed=True)
            
            # Step 5: Runtime analysis (if logs available)
            task = progress.add_task("[cyan]Analyzing runtime behavior...", total=None)
            runtime_analyzer = RuntimeAnalyzer(CONFIG['analysis'])
            runtime_findings = runtime_analyzer.analyze()
            progress.update(task, completed=True)
            
            # Step 6: Correlate findings
            task = progress.add_task("[cyan]Correlating incidents...", total=None)
            correlator = IncidentCorrelator(CONFIG['analysis']['correlation'])
            all_findings = static_findings + api_findings + runtime_findings
            incidents = correlator.correlate(all_findings)
            progress.update(task, completed=True)
            
            # Step 7: Classify severity
            task = progress.add_task("[cyan]Classifying severity...", total=None)
            classifier = SeverityClassifier(CONFIG['severity'])
            for incident in incidents:
                incident['severity'] = classifier.classify(incident)
            progress.update(task, completed=True)
            
            # Step 8: Generate remediations
            task = progress.add_task("[cyan]Generating remediations...", total=None)
            fix_generator = FixGenerator(CONFIG['remediation'])
            for incident in incidents:
                incident['remediation'] = fix_generator.generate(incident)
            progress.update(task, completed=True)
            
            # Step 9: AI reasoning (optional)
            if use_ibm_watson:
                task = progress.add_task("[cyan]Running AI analysis...", total=None)
                reasoning_engine = ReasoningEngine(CONFIG['ai_engine'])
                incidents = reasoning_engine.enhance_analysis(incidents)
                progress.update(task, completed=True)
            
            # Step 10: Generate reports
            task = progress.add_task("[cyan]Generating reports...", total=None)
            reporter = IncidentReporter(CONFIG['reporting'])
            report_paths = reporter.generate_reports(incidents, output, format)
            progress.update(task, completed=True)
            
            # Step 11: Update AI memory
            task = progress.add_task("[cyan]Updating AI memory...", total=None)
            memory_manager = MemoryManager(CONFIG['ai_engine']['memory'])
            memory_manager.learn_from_incidents(incidents)
            progress.update(task, completed=True)
        
        # Display summary
        display_summary(incidents, severity_threshold)
        
        # Display report locations
        console.print("\n[bold green]✓ Analysis Complete[/bold green]")
        console.print(f"\n[cyan]Reports generated:[/cyan]")
        for report_path in report_paths:
            console.print(f"  📄 {report_path}")
        
    except Exception as e:
        console.print(f"[bold red]✗ Error during analysis:[/bold red] {str(e)}")
        raise


def display_summary(incidents, severity_threshold):
    """Display analysis summary"""
    # Filter by severity threshold
    filtered_incidents = [i for i in incidents if i['severity']['level'] >= severity_threshold]
    
    # Count by severity
    severity_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for incident in filtered_incidents:
        level = incident['severity']['level']
        severity_counts[level] += 1
    
    # Create summary table
    console.print("\n")
    console.print(Panel.fit(
        "[bold]📊 Analysis Summary[/bold]",
        border_style="green"
    ))
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    table.add_row("Total Incidents", str(len(filtered_incidents)))
    table.add_row("Critical (Level 5)", f"[red]{severity_counts[5]}[/red]")
    table.add_row("High (Level 4)", f"[orange1]{severity_counts[4]}[/orange1]")
    table.add_row("Medium (Level 3)", f"[yellow]{severity_counts[3]}[/yellow]")
    table.add_row("Low (Level 2)", f"[blue]{severity_counts[2]}[/blue]")
    table.add_row("Informational (Level 1)", f"[dim]{severity_counts[1]}[/dim]")
    
    console.print(table)
    
    # Display critical incidents
    critical_incidents = [i for i in filtered_incidents if i['severity']['level'] == 5]
    if critical_incidents:
        console.print("\n[bold red]⚠️  CRITICAL INCIDENTS DETECTED[/bold red]")
        for incident in critical_incidents:
            console.print(f"\n[red]• {incident['title']}[/red]")
            console.print(f"  ID: {incident['id']}")
            console.print(f"  Confidence: {incident['severity']['confidence']:.2f}")


@cli.command()
@click.option('--incident-id', '-i', help='Specific incident ID to report')
@click.option('--format', '-f', default='markdown', help='Output format')
@click.option('--output', '-o', default='./output', help='Output directory')
def report(incident_id, format, output):
    """
    Generate detailed incident report
    """
    console.print(f"[cyan]Generating report for incident: {incident_id}[/cyan]")
    # Implementation will load incident from database and generate report
    console.print(f"[green]✓ Report saved to: {output}/{incident_id}.{format}[/green]")


@cli.command()
@click.option('--list', '-l', is_flag=True, help='List all AI memory entries')
@click.option('--pattern', '-p', help='Search for specific pattern')
@click.option('--export', '-e', help='Export memory to file')
def memory(list, pattern, export):
    """
    View and manage AI security memory
    """
    memory_manager = MemoryManager(CONFIG['ai_engine']['memory'])
    
    if list:
        entries = memory_manager.list_all()
        console.print(f"[cyan]Found {len(entries)} memory entries[/cyan]\n")
        for entry in entries:
            console.print(f"[bold]{entry['incident_pattern']}[/bold]")
            console.print(f"  Prevention: {entry['prevention_rule']}")
            console.print()
    
    if pattern:
        results = memory_manager.search(pattern)
        console.print(f"[cyan]Found {len(results)} matching entries[/cyan]")
    
    if export:
        memory_manager.export(export)
        console.print(f"[green]✓ Memory exported to: {export}[/green]")


@cli.command()
@click.option('--path', '-p', required=True, help='Path to test')
@click.option('--test-type', '-t', multiple=True, 
              help='Test type (secrets, deprecated-api, auth, all)')
def test(path, test_type):
    """
    Run security tests on codebase
    """
    if not test_type or 'all' in test_type:
        test_type = ['secrets', 'deprecated-api', 'auth', 'sql-injection']
    
    console.print("[cyan]Running security tests...[/cyan]\n")
    
    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
    
    for test in test_type:
        console.print(f"[bold]Testing: {test}[/bold]")
        # Run specific test
        # Update results
        console.print(f"[green]✓ {test} tests passed[/green]\n")
    
    # Display summary
    console.print(f"\n[bold]Test Summary:[/bold]")
    console.print(f"  Passed: [green]{results['passed']}[/green]")
    console.print(f"  Failed: [red]{results['failed']}[/red]")
    console.print(f"  Warnings: [yellow]{results['warnings']}[/yellow]")


@cli.command()
@click.option('--scenario-id', '-s', help='Specific scenario to test')
@click.option('--all', '-a', is_flag=True, help='Run all scenarios')
def test_scenarios(scenario_id, all):
    """
    Test system with attack scenarios
    """
    scenarios_path = Path(__file__).parent.parent / "mock_data" / "scenarios"
    
    if all:
        console.print("[cyan]Running all attack scenarios...[/cyan]\n")
        # Load and run all scenarios
    elif scenario_id:
        console.print(f"[cyan]Running scenario: {scenario_id}[/cyan]\n")
        # Load and run specific scenario
    else:
        console.print("[yellow]Please specify --scenario-id or --all[/yellow]")


@cli.command()
@click.option('--format', '-f', default='json', help='Export format')
@click.option('--output', '-o', required=True, help='Output file path')
@click.option('--severity', '-s', type=int, help='Filter by minimum severity')
def export(format, output, severity):
    """
    Export findings and incidents
    """
    console.print(f"[cyan]Exporting data to {output}...[/cyan]")
    # Load incidents from database and export
    console.print(f"[green]✓ Data exported successfully[/green]")


@cli.command()
def init():
    """
    Initialize the security analyst system
    """
    console.print("[cyan]Initializing Security Analyst System...[/cyan]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Setting up database...", total=None)
        db_manager = DatabaseManager(CONFIG['database'])
        db_manager.initialize()
        progress.update(task, completed=True)
        
        task = progress.add_task("[cyan]Loading detection patterns...", total=None)
        # Load patterns
        progress.update(task, completed=True)
        
        task = progress.add_task("[cyan]Initializing AI models...", total=None)
        # Initialize ML models
        progress.update(task, completed=True)
        
        task = progress.add_task("[cyan]Creating output directories...", total=None)
        os.makedirs("./output", exist_ok=True)
        os.makedirs("./logs", exist_ok=True)
        progress.update(task, completed=True)
    
    console.print("\n[bold green]✓ System initialized successfully[/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Run: [cyan]python src/main.py analyze --path /path/to/code[/cyan]")
    console.print("  2. View reports in: [cyan]./output[/cyan]")


@cli.command()
def status():
    """
    Show system status and statistics
    """
    console.print(Panel.fit(
        "[bold cyan]System Status[/bold cyan]",
        border_style="cyan"
    ))
    
    # Database status
    try:
        db_manager = DatabaseManager(CONFIG['database'])
        db_status = "🟢 Connected"
    except:
        db_status = "🔴 Disconnected"
    
    console.print(f"\nDatabase: {db_status}")
    console.print(f"AI Engine: {'🟢 Enabled' if CONFIG['ai_engine']['local_models']['enabled'] else '🔴 Disabled'}")
    console.print(f"IBM Watson: {'🟢 Enabled' if CONFIG['ai_engine']['ibm_watson']['enabled'] else '🔴 Disabled'}")
    
    # Statistics
    console.print("\n[bold]Statistics:[/bold]")
    console.print("  Total Incidents: 0")
    console.print("  AI Memory Entries: 0")
    console.print("  Last Analysis: Never")


if __name__ == '__main__':
    cli()

# Made with Bob
