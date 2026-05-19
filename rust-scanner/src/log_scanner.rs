use regex::Regex;
use anyhow::Result;
use crate::models::{Finding, FindingType, FindingCategory, Severity};
use crate::file_walker::ScannableFile;

pub struct LogScanner {
    patterns: Vec<LogPattern>,
}

struct LogPattern {
    name: &'static str,
    regex: Regex,
    severity: Severity,
}

impl LogScanner {
    pub fn new() -> Result<Self> {
        let patterns = vec![
            LogPattern {
                name: "Logging sensitive data",
                regex: Regex::new(r#"(?i)(log|logger|console|print|echo)\s*\.\s*(info|debug|warn|error)?\s*\(.*?(password|secret|token|key|credential)"#)?,
                severity: Severity::High,
            },
            LogPattern {
                name: "Logging user data",
                regex: Regex::new(r#"(?i)(log|logger|console|print)\s*\.\s*(info|debug|warn|error)?\s*\(.*?(email|ssn|credit_card|phone)"#)?,
                severity: Severity::Medium,
            },
            LogPattern {
                name: "Logging API keys",
                regex: Regex::new(r#"(?i)(log|logger|console|print)\s*\.\s*(info|debug|warn|error)?\s*\(.*?(api[_-]?key|apikey)"#)?,
                severity: Severity::Critical,
            },
            LogPattern {
                name: "Logging authentication tokens",
                regex: Regex::new(r#"(?i)(log|logger|console|print)\s*\.\s*(info|debug|warn|error)?\s*\(.*?(auth|bearer|jwt)"#)?,
                severity: Severity::High,
            },
            LogPattern {
                name: "Logging database credentials",
                regex: Regex::new(r#"(?i)(log|logger|console|print)\s*\.\s*(info|debug|warn|error)?\s*\(.*?(db_password|database_url|connection_string)"#)?,
                severity: Severity::Critical,
            },
            LogPattern {
                name: "Debug logging in production code",
                regex: Regex::new(r#"(?i)(log|logger|console)\s*\.\s*debug\s*\("#)?,
                severity: Severity::Low,
            },
            LogPattern {
                name: "Printing request headers",
                regex: Regex::new(r#"(?i)(log|logger|console|print)\s*\.\s*(info|debug|warn|error)?\s*\(.*?(headers|request\.headers)"#)?,
                severity: Severity::Medium,
            },
            LogPattern {
                name: "Logging full request body",
                regex: Regex::new(r#"(?i)(log|logger|console|print)\s*\.\s*(info|debug|warn|error)?\s*\(.*?(request\.body|req\.body|body)"#)?,
                severity: Severity::Medium,
            },
        ];

        Ok(Self { patterns })
    }

    pub fn scan(&self, file: &ScannableFile, finding_counter: &mut usize) -> Result<Vec<Finding>> {
        let content = file.read_content()?;
        let mut findings = Vec::new();

        // Only scan code files
        let file_path = file.relative_path();
        let is_code_file = file_path.ends_with(".py") 
            || file_path.ends_with(".js") 
            || file_path.ends_with(".ts")
            || file_path.ends_with(".go")
            || file_path.ends_with(".java")
            || file_path.ends_with(".rb")
            || file_path.ends_with(".php")
            || file_path.ends_with(".cs");

        if !is_code_file {
            return Ok(findings);
        }

        for (line_num, line) in content.lines().enumerate() {
            for pattern in &self.patterns {
                if let Some(captures) = pattern.regex.captures(line) {
                    let evidence = captures.get(0)
                        .map(|m| m.as_str())
                        .unwrap_or("");

                    // Extract what's being logged if possible
                    let logged_item = captures.get(3)
                        .map(|m| m.as_str())
                        .unwrap_or("sensitive data");

                    *finding_counter += 1;

                    let finding = Finding::new(
                        format!("FIND-{:03}", finding_counter),
                        file.repo_name.clone(),
                        FindingType::SensitiveLogExposure,
                        FindingCategory::Logging,
                        pattern.severity.clone(),
                        file.relative_path(),
                        (line_num + 1) as u32,
                        format!("{}: {}", pattern.name, logged_item),
                        evidence.chars().take(50).collect::<String>(),
                    );

                    findings.push(finding);
                }
            }
        }

        Ok(findings)
    }
}

// Made with Bob
