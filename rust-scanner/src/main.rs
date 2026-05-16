mod models;
mod file_walker;
mod secret_scanner;
mod api_scanner;
mod infra_scanner;
mod log_scanner;

use clap::{Parser, Subcommand};
use anyhow::Result;
use std::path::PathBuf;

use file_walker::FileWalker;
use secret_scanner::SecretScanner;
use api_scanner::ApiScanner;
use infra_scanner::InfraScanner;
use log_scanner::LogScanner;
use models::Finding;

#[derive(Parser)]
#[command(name = "bob-scanner")]
#[command(about = "Bob Sentinel Security Scanner", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Scan repositories for security issues
    Scan {
        /// Paths to scan (can be multiple repositories)
        #[arg(long = "path", required = true, num_args = 1..)]
        paths: Vec<PathBuf>,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Scan { paths } => {
            scan_repositories(paths)?;
        }
    }

    Ok(())
}

fn scan_repositories(paths: Vec<PathBuf>) -> Result<()> {
    // Initialize scanners
    let secret_scanner = SecretScanner::new()?;
    let api_scanner = ApiScanner::new()?;
    let infra_scanner = InfraScanner::new()?;
    let log_scanner = LogScanner::new()?;

    // Walk all files
    let walker = FileWalker::new(paths);
    let files = walker.walk()?;

    // Collect all findings
    let mut all_findings: Vec<Finding> = Vec::new();
    let mut finding_counter = 0;

    for file in &files {
        // Secret scanning
        match secret_scanner.scan(file, &mut finding_counter) {
            Ok(findings) => all_findings.extend(findings),
            Err(e) => {
                eprintln!("Warning: Failed to scan {} for secrets: {}", file.path.display(), e);
            }
        }

        // API scanning
        match api_scanner.scan(file, &mut finding_counter) {
            Ok(findings) => all_findings.extend(findings),
            Err(e) => {
                eprintln!("Warning: Failed to scan {} for APIs: {}", file.path.display(), e);
            }
        }

        // Infrastructure scanning
        match infra_scanner.scan(file, &mut finding_counter) {
            Ok(findings) => all_findings.extend(findings),
            Err(e) => {
                eprintln!("Warning: Failed to scan {} for infra issues: {}", file.path.display(), e);
            }
        }

        // Log scanning
        match log_scanner.scan(file, &mut finding_counter) {
            Ok(findings) => all_findings.extend(findings),
            Err(e) => {
                eprintln!("Warning: Failed to scan {} for log issues: {}", file.path.display(), e);
            }
        }
    }

    // Output findings as JSON to stdout
    let json_output = serde_json::to_string_pretty(&all_findings)?;
    println!("{}", json_output);

    Ok(())
}

// Made with Bob
